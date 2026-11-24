# Runbook: Connect a Test Entra ID Tenant to a Test GitHub Organization (SAML SSO + SCIM + Team Sync)

**Model:** Organization-level SAML SSO + SCIM (users keep personal GitHub accounts; Entra gates org access)
**Environment:** TEST ONLY — test Entra tenant ↔ test GitHub org
**Executor:** Human operator + Claude Code (CLI steps marked `[CLI]`, browser-only steps marked `[UI]`)

---

## 0. Variables

Fill these in before starting. Claude Code should export them in its shell.

```bash
export TENANT_ID="<entra-test-tenant-id>"
export GH_ORG="<test-github-org-name>"          # e.g. contoso-test
export APP_NAME="GitHub Test SSO - ${GH_ORG}"
export TEST_GROUP="GH-Test-Developers"          # Entra group to map to a GitHub team
export GH_TEAM="test-developers"                # GitHub team slug
export TEST_REPO="sso-test-repo"                # repo used to validate team-based access
```

Derived SAML values:

| Field | Value |
|---|---|
| Identifier (Entity ID) | `https://github.com/orgs/${GH_ORG}` |
| Reply URL (ACS) | `https://github.com/orgs/${GH_ORG}/saml/consume` |
| Sign-on URL | `https://github.com/orgs/${GH_ORG}/sso` |
| SCIM Tenant URL | `https://api.github.com/scim/v2/organizations/${GH_ORG}` |

---

## 1. Prerequisites

| # | Requirement | Check |
|---|---|---|
| 1.1 | Test GitHub org is on **GitHub Enterprise Cloud** (a free 30-day trial works). Free/Team plans can't enable SAML. | Org Settings → Billing and plans |
| 1.2 | Operator is an **Owner** of the test GitHub org | `gh api /orgs/$GH_ORG/memberships/$(gh api /user -q .login) -q .role` → `admin` |
| 1.3 | Operator has **Global Admin**, **Cloud Application Admin** or **Application Admin** in the test tenant | Entra → Roles |
| 1.4 | Entra **P1/P2** license if you assign *groups* to the app (Free tier only allows assigning individual users) | Entra → Licenses |
| 1.5 | At least 2 test users in Entra, each with their own personal GitHub account | — |
| 1.6 | Tools installed: `az` (Azure CLI), `gh` (GitHub CLI), `jq` | `az version; gh --version; jq --version` |
| 1.7 | A second org owner, or saved recovery codes (step 4.4), so you can't get locked out | — |

```bash
# [CLI] Authenticate
az login --tenant "$TENANT_ID" --allow-no-subscriptions
gh auth login --scopes "admin:org,repo,read:user"
```

---

## 2. Prepare the test GitHub side

```bash
# [CLI] Create a test repo and team for access validation
gh repo create "$GH_ORG/$TEST_REPO" --private --add-readme
gh api -X POST /orgs/$GH_ORG/teams -f name="$GH_TEAM" -f privacy=closed
gh api -X PUT /orgs/$GH_ORG/teams/$GH_TEAM/repos/$GH_ORG/$TEST_REPO -f permission=push

# [CLI] Record baseline membership (to compare later)
gh api /orgs/$GH_ORG/members --paginate -q '.[].login' > baseline_members.txt
gh api /orgs/$GH_ORG/outside_collaborators --paginate -q '.[].login' > baseline_outside_collabs.txt
```

---

## 3. Create the enterprise application in Entra

### 3.1 Instantiate the gallery app `[CLI]`

```bash
# Find the gallery template ID for "GitHub Enterprise Cloud - Organization"
TEMPLATE_ID=$(az rest --method GET \
  --uri "https://graph.microsoft.com/v1.0/applicationTemplates?\$filter=displayName eq 'GitHub Enterprise Cloud - Organization'" \
  -q "value[0].id" -o tsv)
echo "Template: $TEMPLATE_ID"

# Instantiate it (creates both the application and the service principal)
RESULT=$(az rest --method POST \
  --uri "https://graph.microsoft.com/v1.0/applicationTemplates/$TEMPLATE_ID/instantiate" \
  --body "{\"displayName\": \"$APP_NAME\"}")

export APP_OBJECT_ID=$(echo "$RESULT" | jq -r .application.id)
export APP_ID=$(echo "$RESULT" | jq -r .application.appId)
export SP_ID=$(echo "$RESULT" | jq -r .servicePrincipal.id)
echo "App object: $APP_OBJECT_ID  AppId: $APP_ID  SP: $SP_ID"
```

> Graph can take 10–30 seconds to replicate. If the next calls return 404, wait and retry.

### 3.2 Configure SAML `[CLI]`

```bash
# Set SSO mode to SAML
az rest --method PATCH \
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/$SP_ID" \
  --body '{"preferredSingleSignOnMode": "saml"}'

# Set Identifier, Reply URL, and Sign-on URL
az rest --method PATCH \
  --uri "https://graph.microsoft.com/v1.0/applications/$APP_OBJECT_ID" \
  --body "{
    \"identifierUris\": [\"https://github.com/orgs/$GH_ORG\"],
    \"web\": {
      \"redirectUris\": [\"https://github.com/orgs/$GH_ORG/saml/consume\"]
    }
  }"

az rest --method PATCH \
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/$SP_ID" \
  --body "{\"loginUrl\": \"https://github.com/orgs/$GH_ORG/sso\"}"

# Create a SAML signing certificate (3-year expiry)
az rest --method POST \
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/$SP_ID/addTokenSigningCertificate" \
  --body "{\"displayName\": \"CN=$APP_NAME\", \"endDateTime\": \"$(date -u -d '+3 years' +%Y-%m-%dT%H:%M:%SZ)\"}" \
  > signing_cert.json
```

> **Fallback `[UI]`:** If any Graph call fails, do the same in the portal: Entra → Enterprise applications → *APP_NAME* → Single sign-on → SAML → edit "Basic SAML Configuration".

### 3.3 Collect the values GitHub needs `[UI]`

In Entra → Enterprise applications → *APP_NAME* → Single sign-on:

| Entra field | Goes into GitHub field |
|---|---|
| **Login URL** (`https://login.microsoftonline.com/<tenant>/saml2`) | Sign on URL |
| **Microsoft Entra Identifier** (`https://sts.windows.net/<tenant>/`) | Issuer |
| **Certificate (Base64)** → Download | Public certificate (paste the full PEM text) |

```bash
# [CLI] Pre-fill the tenant-based values
echo "Sign on URL: https://login.microsoftonline.com/$TENANT_ID/saml2"
echo "Issuer:      https://sts.windows.net/$TENANT_ID/"
```

### 3.4 Create the test group and assign it `[CLI]`

```bash
GROUP_ID=$(az ad group create --display-name "$TEST_GROUP" --mail-nickname "$TEST_GROUP" -q id -o tsv)

# Add test users (repeat for each)
az ad group member add --group "$GROUP_ID" --member-id "<test-user-object-id>"

# Assign the group to the app (requires P1/P2; without it, assign users individually)
APP_ROLE_ID=$(az ad sp show --id "$SP_ID" -q "appRoles[?displayName=='User'].id | [0]" -o tsv)
[ -z "$APP_ROLE_ID" ] && APP_ROLE_ID="00000000-0000-0000-0000-000000000000"   # default access

az rest --method POST \
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/$SP_ID/appRoleAssignedTo" \
  --body "{\"principalId\": \"$GROUP_ID\", \"resourceId\": \"$SP_ID\", \"appRoleId\": \"$APP_ROLE_ID\"}"
```

---

## 4. Enable SAML SSO in GitHub `[UI]` — no API exists for this step

1. Go to `https://github.com/organizations/$GH_ORG/settings/security`.
2. Under **SAML single sign-on**, check **Enable SAML authentication**.
3. Enter:
   - **Sign on URL**: the Entra Login URL
   - **Issuer**: the Microsoft Entra Identifier
   - **Public certificate**: the Base64 PEM contents
   - Signature / Digest method: leave the defaults (RSA-SHA256 / SHA256)
4. Click **Test SAML configuration**. You should be redirected to Entra and back with a success message.
5. **Save**, then **download and store the recovery codes** somewhere outside the test environment.
6. **Do NOT check "Require SAML SSO" yet.**

**Checkpoint:** A test user browses to `https://github.com/orgs/$GH_ORG/sso`, signs in with Entra, and gets the "linked identity" confirmation.

```bash
# [CLI] Verify linked identities
gh api graphql -f query='
query($org: String!) {
  organization(login: $org) {
    samlIdentityProvider {
      ssoUrl
      externalIdentities(first: 50) {
        nodes { user { login } samlIdentity { nameId } }
      }
    }
  }
}' -f org="$GH_ORG"
```

---

## 5. Configure SCIM provisioning `[UI]`

The org SCIM connection uses an OAuth authorization flow from Entra, so this step is done in the portal.

1. Entra → Enterprise applications → *APP_NAME* → **Provisioning** → Get started.
2. Set **Provisioning Mode** to **Automatic**.
3. Set **Tenant URL** to `https://api.github.com/scim/v2/organizations/<GH_ORG>`.
4. **Secret Token**: click **Authorize** and sign in to GitHub as an org owner, then grant access to the org. If the page shows a token field instead, use a classic PAT with the `admin:org` scope that has been **authorized for SAML SSO** for this org.
5. Click **Test Connection**. It should succeed.
6. **Mappings**: keep the defaults, and make sure `userName` / `externalId` / `emails` are mapped. Use the same NameID source attribute as SAML (usually `user.userprincipalname` or `user.mail`).
7. **Scope**: "Sync only assigned users and groups".
8. Set **Provisioning Status** to **On** and save.
9. Optional: use **Provision on demand** for one test user to avoid waiting for the ~40-minute cycle.

```bash
# [CLI] Verify SCIM identities exist on the GitHub side
gh api /scim/v2/organizations/$GH_ORG/Users -q '.Resources[] | {userName, active, id}'

# [CLI] Check the Entra provisioning job status
JOB_ID=$(az rest --method GET \
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/$SP_ID/synchronization/jobs" -q "value[0].id" -o tsv)
az rest --method GET \
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/$SP_ID/synchronization/jobs/$JOB_ID" \
  -q "status"
```

> SCIM sends an **org invitation** to provisioned users. They still have to accept it and complete SSO with their personal GitHub account.

---

## 6. Configure team synchronization `[UI]`

1. Go to `https://github.com/organizations/$GH_ORG/settings/security` → **Team synchronization** → **Enable for Azure AD / Entra ID**.
2. Sign in as an Entra admin and grant consent (this creates a GitHub team-sync app in the tenant).
3. Go to the team page `https://github.com/orgs/$GH_ORG/teams/$GH_TEAM` → Settings → **Identity Provider Groups** → select `$TEST_GROUP` → Save changes.

```bash
# [CLI] Verify the group mapping and resulting team membership
gh api /orgs/$GH_ORG/teams/$GH_TEAM/team-sync/group-mappings
gh api /orgs/$GH_ORG/teams/$GH_TEAM/members -q '.[].login'
```

> Team sync can take up to ~1 hour. When it runs, members are added to or removed from the team based on the Entra group.

---

## 7. Validation tests

| # | Test | Expected result |
|---|---|---|
| 7.1 | Test user A (in `$TEST_GROUP`) opens `https://github.com/$GH_ORG/$TEST_REPO` | Redirected to Entra SSO, then has push access |
| 7.2 | Test user B (not assigned to the app) tries `https://github.com/orgs/$GH_ORG/sso` | Entra denies with "user not assigned" (AADSTS50105) |
| 7.3 | User A runs `git clone` with a PAT or SSH key **not** authorized for SSO | Fails with an SSO authorization error |
| 7.4 | User A authorizes the PAT/SSH key for SSO (Settings → Developer settings / SSH keys → Configure SSO), then clones | Succeeds |
| 7.5 | Remove user A from `$TEST_GROUP` in Entra and wait for sync / provision on demand | User A is removed from the team and the org |
| 7.6 | Add user A back | User A is re-invited and team access is restored |
| 7.7 | Check the audit log | SSO and SCIM events are recorded |

```bash
# [CLI] 7.7 — audit log (Enterprise Cloud)
gh api "/orgs/$GH_ORG/audit-log?phrase=action:org.saml" -q '.[] | {action, actor, created_at}' 2>/dev/null \
  || echo "Check audit log in UI: Org Settings → Logs → Audit log"
```

---

## 8. Enforce SAML SSO `[UI]`

Do this only after 7.1–7.6 pass.

1. Compare the linked identities from step 4 with `baseline_members.txt`. **Any member without a linked identity will be removed when you enforce.**
2. Go to Org Settings → Authentication security → check **Require SAML SSO authentication** → review the list of members who will be removed → Save.
3. Re-run test 7.1.

> Outside collaborators (see `baseline_outside_collabs.txt`) are **not** covered by SAML. Review them separately.

---

## 9. Rollback

| Situation | Action |
|---|---|
| SAML test fails | Fix the values and re-test. Nothing is enforced yet, so there's no impact. |
| Locked out after enforcement | Use a recovery code at `https://github.com/orgs/$GH_ORG/sso` → "Use a recovery code" |
| Need to fully back out | GitHub: Org Settings → Authentication security → uncheck Enable SAML. Entra: Provisioning → Status **Off**, then delete the app (`az ad sp delete --id $SP_ID; az ad app delete --id $APP_ID`). Disable team sync. |
| Members removed during enforcement | Re-invite them. GitHub keeps their org access settings for reinstatement for ~3 months. |

---

## 10. Notes for production (beyond this test)

- Users must authorize every PAT and SSH key for SSO. Warn CI/CD owners, and plan for GitHub Apps instead of PATs.
- Track the signing certificate expiry (step 3.2) and set a rotation reminder.
- If you need Entra Conditional Access, or want Entra to own GitHub accounts, evaluate **Enterprise Managed Users (EMU) with OIDC**. That requires a **new** enterprise account and moving the repos.
- Don't mix Okta and Entra for SSO and SCIM. GitHub doesn't support that combination.
- Make it a policy to review outside collaborators, since SAML/SCIM doesn't cover them.

---

## Sign-off

| Step | Done by | Date | Result |
|---|---|---|---|
| 1 Prereqs | | | |
| 3 Entra app | | | |
| 4 SAML enabled | | | |
| 5 SCIM | | | |
| 6 Team sync | | | |
| 7 Validation | | | |
| 8 Enforced | | | |
