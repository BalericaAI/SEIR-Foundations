      *> ============================================================
      *>                       BALERICA AI
      *>                    SEIR FOUNDATIONS
      *> ============================================================
      *>
      *>                 BALERICA LEGACY BANK
      *>                  ACCOUNT_LOOKUP.COB
      *>
      *> Chewbacca says:
      *>
      *>     "RRRRAAAWWWRRR!"
      *>
      *> Translation:
      *>
      *>     Welcome to COBOL.
      *>
      *>     This language is older than the moon landing.
      *>
      *>     It still moves most of the world's money.
      *>
      *>     Respect it.
      *>
      *> ------------------------------------------------------------
      *>
      *> WHAT THIS PROGRAM DOES
      *>
      *>     Reads one account id from the command line.
      *>
      *>     Scans the fixed-width ledger file:
      *>
      *>         data/accounts.dat
      *>
      *>     Prints the account as KEY=VALUE lines so that
      *>     modern systems (FastAPI) can parse the output.
      *>
      *> RETURN CODES (the mainframe way)
      *>
      *>     0  = account found
      *>     4  = account not found
      *>     8  = missing account id argument
      *>     12 = ledger file could not be opened
      *>
      *> RUN IT YOURSELF
      *>
      *>     cd /opt/balerica-bank
      *>     ./cobol/bin/account_lookup 100001
      *>
      *> ============================================================

       IDENTIFICATION DIVISION.
       PROGRAM-ID. ACCOUNT-LOOKUP.

      *> ------------------------------------------------------------
      *> ENVIRONMENT DIVISION
      *>
      *> Chewbacca says: "Rrrrrrrgh..."
      *>
      *> Translation:
      *>
      *>     COBOL declares its files up front.
      *>
      *>     No surprises. No hidden I/O.
      *>
      *>     The record layout IS the schema.
      *> ------------------------------------------------------------

       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT ACCOUNTS-FILE ASSIGN TO "data/accounts.dat"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS WS-FILE-STATUS.

       DATA DIVISION.
       FILE SECTION.

      *> ------------------------------------------------------------
      *> THE LEDGER RECORD
      *>
      *>     Fixed width. Every byte has a job.
      *>
      *>     Columns  1-6   account id
      *>     Columns  7-36  customer name
      *>     Columns 37-44  status
      *>     Columns 45-56  balance  (implied decimal: 9(10)V99)
      *>     Columns 57-59  currency
      *> ------------------------------------------------------------

       FD  ACCOUNTS-FILE.
       01  ACCOUNT-RECORD.
           05  ACCT-ID        PIC X(6).
           05  ACCT-NAME      PIC X(30).
           05  ACCT-STATUS    PIC X(8).
           05  ACCT-BALANCE   PIC 9(10)V99.
           05  ACCT-CURRENCY  PIC X(3).

       WORKING-STORAGE SECTION.
       01  WS-FILE-STATUS     PIC XX   VALUE "00".
       01  WS-TARGET-ID       PIC X(6) VALUE SPACES.
       01  WS-FOUND           PIC X    VALUE "N".
       01  WS-EOF             PIC X    VALUE "N".
       01  WS-BALANCE-EDIT    PIC Z(9)9.99.

       PROCEDURE DIVISION.
       MAIN-LOGIC.

      *>   The account id arrives from the command line.
           ACCEPT WS-TARGET-ID FROM COMMAND-LINE

           IF WS-TARGET-ID = SPACES
               DISPLAY "ERROR=MISSING ACCOUNT ID"
               MOVE 8 TO RETURN-CODE
               STOP RUN
           END-IF

           OPEN INPUT ACCOUNTS-FILE
           IF WS-FILE-STATUS NOT = "00"
               DISPLAY "ERROR=CANNOT OPEN data/accounts.dat"
               DISPLAY "FILE-STATUS=" WS-FILE-STATUS
               MOVE 12 TO RETURN-CODE
               STOP RUN
           END-IF

      *>   Sequential scan. On a mainframe this file would be
      *>   indexed (VSAM). Today we read it the honest way.
           PERFORM UNTIL WS-EOF = "Y" OR WS-FOUND = "Y"
               READ ACCOUNTS-FILE
                   AT END
                       MOVE "Y" TO WS-EOF
                   NOT AT END
                       IF ACCT-ID = WS-TARGET-ID
                           MOVE "Y" TO WS-FOUND
                       END-IF
               END-READ
           END-PERFORM

           CLOSE ACCOUNTS-FILE

           IF WS-FOUND = "Y"
               MOVE ACCT-BALANCE TO WS-BALANCE-EDIT
               DISPLAY "ACCOUNT=" ACCT-ID
               DISPLAY "NAME=" FUNCTION TRIM(ACCT-NAME)
               DISPLAY "STATUS=" FUNCTION TRIM(ACCT-STATUS)
               DISPLAY "BALANCE=" FUNCTION TRIM(WS-BALANCE-EDIT)
               DISPLAY "CURRENCY=" ACCT-CURRENCY
               MOVE 0 TO RETURN-CODE
           ELSE
               DISPLAY "ERROR=ACCOUNT NOT FOUND"
               DISPLAY "ACCOUNT=" WS-TARGET-ID
               MOVE 4 TO RETURN-CODE
           END-IF

           STOP RUN.
