       >>SOURCE FORMAT FREE
identification division.
program-id. financial.
environment division.
configuration section.
repository. function all intrinsic.
data division.
working-storage section.
01 incoming-line pic x(256).
01 operation pic x(24).
01 arg-a pic x(32).
01 arg-b pic x(32).
01 arg-c pic x(32).
01 principal usage comp-3 pic 9(10)v99.
01 annual-rate usage comp-3 pic 9(3)v99.
01 time-count binary-long.
01 periodic-rate usage comp-2.
01 loan-result usage comp-2.
01 interest-result usage comp-3 pic 9(12)v99.
01 total-result usage comp-3 pic 9(12)v99.
01 money-output pic Z(11)9.99.
01 total-output pic Z(11)9.99.
procedure division.
    accept incoming-line
    unstring incoming-line delimited by '|'
        into operation arg-a arg-b arg-c
    end-unstring
    if trim(arg-a) = spaces or trim(arg-b) = spaces
        display 'ERR|missing_arguments'
        move 2 to return-code
        goback
    end-if
    move function numval(trim(arg-a)) to principal
    evaluate trim(operation)
      when 'INTEREST'
        move function numval(trim(arg-b)) to annual-rate
        move function numval(trim(arg-c)) to time-count
        compute interest-result rounded =
            principal * annual-rate * time-count / 100
        compute total-result = principal + interest-result
        move interest-result to money-output
        move total-result to total-output
        display 'OK|' trim(money-output) '|'
            trim(total-output)
      when 'LOAN'
        move function numval(trim(arg-b)) to annual-rate
        move function numval(trim(arg-c)) to time-count
        if time-count <= 0
            display 'ERR|invalid_months'
            move 2 to return-code
            goback
        end-if
        if annual-rate = 0
            compute loan-result = principal / time-count
        else
            compute periodic-rate = annual-rate / 1200
            compute loan-result = principal * periodic-rate /
                (1 - (1 + periodic-rate) ** (0 - time-count))
        end-if
        move 0 to interest-result
        compute interest-result rounded = loan-result
        move interest-result to money-output
        display 'OK|' trim(money-output)
      when 'TRANSFER'
        if principal <= function numval(trim(arg-b))
            display 'OK|APPROVED'
        else
            display 'OK|DECLINED_INSUFFICIENT_FUNDS'
        end-if
      when other
        display 'ERR|unknown_operation'
        move 2 to return-code
    end-evaluate
    goback.
