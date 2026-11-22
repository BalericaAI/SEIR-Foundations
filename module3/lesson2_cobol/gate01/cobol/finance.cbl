       >>SOURCE FORMAT FREE
identification division.
program-id. finance.
environment division.
configuration section.
repository. function all intrinsic.
data division.
working-storage section.
01 op pic x(24).
01 input-a pic x(30).
01 input-b pic x(30).
01 input-n pic x(10).
01 amount-a pic 9(10)v99.
01 amount-b pic 9(10)v99.
01 rate-month pic 9v9(12).
01 factor pic 9(8)v9(12).
01 result-a pic 9(10)v99.
01 result-b pic 9(10)v99.
01 shown-a pic z(10)9.99.
01 shown-b pic z(10)9.99.
01 periods binary-long.
procedure division.
    accept op from argument-value
    accept input-a from argument-value
    accept input-b from argument-value
    accept input-n from argument-value
    if op = "PING"
        display "OK|READY"
        goback
    end-if
    compute amount-a = function numval(input-a)
    compute amount-b = function numval(input-b)
    evaluate op
      when "INTEREST"
        compute periods = function numval(input-n)
        compute result-a rounded =
            amount-a * amount-b * periods / 100
        compute result-b = amount-a + result-a
        move result-a to shown-a
        move result-b to shown-b
        display "OK|" function trim(shown-a) "|"
            function trim(shown-b)
      when "LOAN"
        compute periods = function numval(input-n)
        if amount-b = 0
            compute result-a rounded = amount-a / periods
        else
            compute rate-month = amount-b / 1200
            compute factor = (1 + rate-month) ** periods
            compute result-a rounded = amount-a * rate-month
                * factor / (factor - 1)
        end-if
        move result-a to shown-a
        display "OK|" function trim(shown-a)
      when "TRANSFER"
        if amount-a <= amount-b
            display "OK|APPROVED"
        else
            display "OK|DECLINED"
        end-if
      when other
        display "ERROR|UNKNOWN_OPERATION"
        move 2 to return-code
    end-evaluate
    goback.
