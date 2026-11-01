       >>SOURCE FORMAT FREE
identification division.
program-id. SEIR-FINANCE.
environment division.
configuration section.
repository. function all intrinsic.
data division.
working-storage section.
01 opening-balance pic 9(7)v99 value 12500.00.
01 debit-amount    pic 9(7)v99 value 250.00.
01 closing-balance pic 9(7)v99.
procedure division.
    compute closing-balance = opening-balance - debit-amount
    display 'SEIR COBOL FINANCIAL BATCH v1'
    display 'Opening: USD ' opening-balance
    display 'Debit:   USD ' debit-amount
    display 'Closing: USD ' closing-balance
    if closing-balance not = 12250.00
       display 'INVARIANT FAILED'
       move 12 to return-code
    else
       display 'FINANCIAL INVARIANT PASSED'
       move 0 to return-code
    end-if
    goback.
