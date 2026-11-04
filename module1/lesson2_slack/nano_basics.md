# Nano Survival Guide: Edit, Save, Exit

Last week you survived `vi`. This week you can use `nano`, which is friendlier:
everything you need is printed at the bottom of the screen. You only need three
keystrokes to leave with your work saved.

## The golden sequence: Ctrl+O, Enter, Ctrl+X

To **save and exit** any file in nano:

1. **`Ctrl+O`** — "Write **O**ut" (save). Nano shows
   `File Name to Write: .env` at the bottom.
2. **`Enter`** — confirms the file name. Nano reports `[ Wrote 4 lines ]`.
3. **`Ctrl+X`** — e**X**it back to your terminal prompt.

Say it with me: **Ctrl+O, Enter, Ctrl+X.** Write it on a sticky note. By week
four it will be muscle memory, just like `:wq` became for vi.

## A full worked example

```bash
cd /opt/balerica-bank
nano .env
```

You are now inside nano. Type or fix your settings, then:

- `Ctrl+O` → bottom line asks `File Name to Write: .env` → press `Enter`
- Bottom line confirms: `[ Wrote 4 lines ]`
- `Ctrl+X` → you are back at the `$` prompt

Verify the save actually happened:

```bash
cat .env
```

If you see your changes, they are saved. Seeing is believing.

## Reading nano's bottom menu

The menu shows things like `^O Write Out` and `^X Exit`. The `^` symbol means
**the Ctrl key**, not Shift+6. So `^O` = hold `Ctrl`, press `O`. (And `M-` means
the Alt key, which you won't need this week.)

## Situations that confuse beginners

| What you see | What it means | What to do |
|---|---|---|
| `Save modified buffer?` when pressing `Ctrl+X` | You tried to exit with unsaved changes | Press `Y`, then `Enter` to save; or `N` to throw changes away |
| `[ File '.env' is unwritable ]` | You don't have permission for this file/folder | Exit and reopen with correct ownership, or check you're in the right directory |
| You're stuck and nothing works | You may have pressed `Ctrl+S` (some terminals freeze) | Press `Ctrl+Q` to unfreeze, then carry on |
| Changes "didn't save" | You pressed `Ctrl+O` but not `Enter`, or edited a different file | Run `cat <filename>` to check; note nano shows the filename at the top |
| `nano: command not found` | Nano isn't installed on this instance | `sudo dnf install -y nano` (Amazon Linux) |

## Bonus keys you'll use constantly

- **`Ctrl+K`** — cut (delete) the whole current line
- **`Ctrl+U`** — paste the line(s) you just cut
- **`Ctrl+W`** — search ("**W**here is") — type text, press Enter
- **Arrow keys** — yes, they just work. Welcome to the future.

> **Chewbacca's note:** RRRRAAAWWWRRR. Ctrl+O. Enter. Ctrl+X. Three moves.
> Even a Wookiee remembers three moves.
