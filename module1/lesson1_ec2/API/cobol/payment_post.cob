      *> ============================================================
      *>                       BALERICA AI
      *>                    SEIR FOUNDATIONS
      *> ============================================================
      *>
      *>                 BALERICA LEGACY BANK
      *>                   PAYMENT_POST.COB
      *>
      *> Chewbacca says:
      *>
      *>     "RRRRRAAAAAAAAAAWWWWWRRRR!"
      *>
      *> Translation:
      *>
      *>     This is the program the auditors care about.
      *>
      *>     It validates a payment and appends it to the
      *>     payment journal. Nothing is ever deleted.
      *>
      *>     Banks do not UPDATE history.
      *>
      *>     Banks APPEND history.
      *>
      *> ------------------------------------------------------------
      *>
      *> WHAT THIS PROGRAM DOES
      *>
      *>     Receives a payment instruction as arguments:
      *>
      *>         payment_post TXN-ID ACCOUNT AMOUNT CURRENCY REF
      *>
      *>     Validates it against data/accounts.dat:
      *>
      *>         1. the account must exist
      *>         2. the account must be ACTIVE
      *>         3. the amount must be greater than zero
      *>         4. the account must have sufficient funds
      *>
      *>     Appends the verdict (POSTED or REJECTED) to the
      *>     journal file data/payments.dat, then reports the
      *>     verdict as KEY=VALUE lines for FastAPI to parse.
      *>
      *> RETURN CODES
      *>
      *>     0  = payment POSTED
      *>     4  = REJECTED, account not found
      *>     8  = REJECTED, business rule (funds, status, amount)
      *>     12 = environment problem (files, arguments)
      *>
      *> RUN IT YOURSELF
      *>
      *>     cd /opt/balerica-bank
      *>     ./cobol/bin/payment_post TXN0001 100001 125.50 USD INV-1001
      *>
      *> ============================================================

       IDENTIFICATION DIVISION.
       PROGRAM-ID. PAYMENT-POST.

       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT ACCOUNTS-FILE ASSIGN TO "data/accounts.dat"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS WS-ACCT-FS.
           SELECT OPTIONAL PAYMENTS-FILE
               ASSIGN TO "data/payments.dat"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS WS-PAY-FS.

       DATA DIVISION.
       FILE SECTION.

       FD  ACCOUNTS-FILE.
       01  ACCOUNT-RECORD.
           05  ACCT-ID        PIC X(6).
           05  ACCT-NAME      PIC X(30).
           05  ACCT-STATUS    PIC X(8).
           05  ACCT-BALANCE   PIC 9(10)V99.
           05  ACCT-CURRENCY  PIC X(3).

      *> ------------------------------------------------------------
      *> THE PAYMENT JOURNAL RECORD
      *>
      *>     Columns  1-20  transaction id
      *>     Columns 21-26  account id
      *>     Columns 27-38  amount (implied decimal: 9(10)V99)
      *>     Columns 39-41  currency
      *>     Columns 42-49  verdict (POSTED / REJECTED)
      *>     Columns 50-65  reference
      *> ------------------------------------------------------------

       FD  PAYMENTS-FILE.
       01  PAYMENT-RECORD.
           05  PAY-TXN-ID     PIC X(20).
           05  PAY-ACCT-ID    PIC X(6).
           05  PAY-AMOUNT     PIC 9(10)V99.
           05  PAY-CURRENCY   PIC X(3).
           05  PAY-STATUS     PIC X(8).
           05  PAY-REFERENCE  PIC X(16).

       WORKING-STORAGE SECTION.
       01  WS-ACCT-FS         PIC XX    VALUE "00".
       01  WS-PAY-FS          PIC XX    VALUE "00".
       01  WS-COMMAND-LINE    PIC X(120) VALUE SPACES.
       01  WS-TXN-ID          PIC X(20) VALUE SPACES.
       01  WS-ACCOUNT-ID      PIC X(6)  VALUE SPACES.
       01  WS-AMOUNT-TEXT     PIC X(14) VALUE SPACES.
       01  WS-CURRENCY        PIC X(3)  VALUE SPACES.
       01  WS-REFERENCE       PIC X(16) VALUE SPACES.
       01  WS-AMOUNT          PIC 9(10)V99 VALUE ZERO.
       01  WS-FOUND           PIC X     VALUE "N".
       01  WS-EOF             PIC X     VALUE "N".
       01  WS-VERDICT         PIC X(8)  VALUE "REJECTED".
       01  WS-REASON          PIC X(40) VALUE SPACES.
       01  WS-RETURN          PIC 99    VALUE 8.
       01  WS-AMOUNT-EDIT     PIC Z(9)9.99.

       PROCEDURE DIVISION.
       MAIN-LOGIC.

           PERFORM PARSE-ARGUMENTS
           PERFORM FIND-ACCOUNT
           PERFORM VALIDATE-PAYMENT
           PERFORM WRITE-JOURNAL
           PERFORM REPORT-VERDICT

           MOVE WS-RETURN TO RETURN-CODE
           STOP RUN.

      *> ------------------------------------------------------------
      *> PARSE-ARGUMENTS
      *>
      *> Chewbacca says: "RAAWR?"
      *>
      *> Translation:
      *>
      *>     UNSTRING is COBOL's split().
      *>
      *>     It was splitting strings before your
      *>     favorite language existed.
      *> ------------------------------------------------------------

       PARSE-ARGUMENTS.
           ACCEPT WS-COMMAND-LINE FROM COMMAND-LINE

           UNSTRING WS-COMMAND-LINE DELIMITED BY ALL SPACES
               INTO WS-TXN-ID
                    WS-ACCOUNT-ID
                    WS-AMOUNT-TEXT
                    WS-CURRENCY
                    WS-REFERENCE
           END-UNSTRING

           IF WS-TXN-ID = SPACES
              OR WS-ACCOUNT-ID = SPACES
              OR WS-AMOUNT-TEXT = SPACES
              OR WS-CURRENCY = SPACES
               DISPLAY "STATUS=REJECTED"
               DISPLAY "REASON=MALFORMED REQUEST"
               DISPLAY "USAGE=payment_post TXN ACCT AMOUNT CCY REF"
               MOVE 12 TO RETURN-CODE
               STOP RUN
           END-IF

      *>   NUMVAL turns "125.50" into a real COBOL number.
           COMPUTE WS-AMOUNT = FUNCTION NUMVAL(WS-AMOUNT-TEXT).

       FIND-ACCOUNT.
           OPEN INPUT ACCOUNTS-FILE
           IF WS-ACCT-FS NOT = "00"
               DISPLAY "STATUS=REJECTED"
               DISPLAY "REASON=CANNOT OPEN data/accounts.dat"
               MOVE 12 TO RETURN-CODE
               STOP RUN
           END-IF

           PERFORM UNTIL WS-EOF = "Y" OR WS-FOUND = "Y"
               READ ACCOUNTS-FILE
                   AT END
                       MOVE "Y" TO WS-EOF
                   NOT AT END
                       IF ACCT-ID = WS-ACCOUNT-ID
                           MOVE "Y" TO WS-FOUND
                       END-IF
               END-READ
           END-PERFORM

           CLOSE ACCOUNTS-FILE.

      *> ------------------------------------------------------------
      *> VALIDATE-PAYMENT
      *>
      *> Chewbacca says: "Rrrrrrrgh..."
      *>
      *> Translation:
      *>
      *>     Every rejection has a reason.
      *>
      *>     A bank that cannot explain a rejection
      *>     is a bank with a regulator problem.
      *> ------------------------------------------------------------

       VALIDATE-PAYMENT.
           EVALUATE TRUE
               WHEN WS-FOUND = "N"
                   MOVE "ACCOUNT NOT FOUND" TO WS-REASON
                   MOVE 4 TO WS-RETURN
               WHEN ACCT-STATUS NOT = "ACTIVE"
                   MOVE "ACCOUNT NOT ACTIVE" TO WS-REASON
                   MOVE 8 TO WS-RETURN
               WHEN WS-AMOUNT = ZERO
                   MOVE "AMOUNT MUST BE GREATER THAN ZERO"
                       TO WS-REASON
                   MOVE 8 TO WS-RETURN
               WHEN WS-AMOUNT > ACCT-BALANCE
                   MOVE "INSUFFICIENT FUNDS" TO WS-REASON
                   MOVE 8 TO WS-RETURN
               WHEN OTHER
                   MOVE "POSTED" TO WS-VERDICT
                   MOVE "APPROVED" TO WS-REASON
                   MOVE 0 TO WS-RETURN
           END-EVALUATE.

      *> ------------------------------------------------------------
      *> WRITE-JOURNAL
      *>
      *>     OPEN EXTEND = append only.
      *>
      *>     POSTED and REJECTED both go in the journal.
      *>     The audit trail records everything.
      *> ------------------------------------------------------------

       WRITE-JOURNAL.
           OPEN EXTEND PAYMENTS-FILE
           IF WS-PAY-FS NOT = "00"
               DISPLAY "STATUS=REJECTED"
               DISPLAY "REASON=CANNOT OPEN data/payments.dat"
               MOVE 12 TO RETURN-CODE
               STOP RUN
           END-IF

           MOVE WS-TXN-ID     TO PAY-TXN-ID
           MOVE WS-ACCOUNT-ID TO PAY-ACCT-ID
           MOVE WS-AMOUNT     TO PAY-AMOUNT
           MOVE WS-CURRENCY   TO PAY-CURRENCY
           MOVE WS-VERDICT    TO PAY-STATUS
           MOVE WS-REFERENCE  TO PAY-REFERENCE

           WRITE PAYMENT-RECORD

           CLOSE PAYMENTS-FILE.

       REPORT-VERDICT.
           MOVE WS-AMOUNT TO WS-AMOUNT-EDIT
           DISPLAY "TXN=" FUNCTION TRIM(WS-TXN-ID)
           DISPLAY "ACCOUNT=" WS-ACCOUNT-ID
           DISPLAY "AMOUNT=" FUNCTION TRIM(WS-AMOUNT-EDIT)
           DISPLAY "CURRENCY=" WS-CURRENCY
           DISPLAY "STATUS=" FUNCTION TRIM(WS-VERDICT)
           DISPLAY "REASON=" FUNCTION TRIM(WS-REASON).
