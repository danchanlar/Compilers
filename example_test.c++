program test
{
    declare a,b;
    declare c;

    function increase(in a,inout b)
    {
        function useless()
        {
            function anotheruseless()
            {
                print 1;  // τέλος statements_sequence, όχι ερωτηματικό
            }
            print (1+(+2))*3;  // τέλος statements_sequence, όχι ερωτηματικό
        }
        b := a + 1 ;
        return a + 10;  // τέλος statements_sequence, όχι ερωτηματικό
    }

    a := 1 ;
    b := 2 + a * a / (2 - a - (2*a));
    c := increase(in a, inout b);
    b := 1;
    while b<10
        if b<>22 or (b>=23 and b<=24)
            b := b+1;     // χρειαζεται ερωτηματικό,
                          // έχουμε στη σειρά εκχώρηση, while, εκχώρηση
    input b;
    c := 12 + (+12);

    switchcase
        when a=1 : a:=a+1   // τέλος statements_sequence, όχι ερωτηματικό
        when a=2 : a:=a+2   // τέλος statements_sequence, όχι ερωτηματικό
        when a=3 : {
                        a:=a+1;
                        a:=a+2  // τέλος statements_sequence, όχι ερωτηματικό
                   }
        default:   a:=a+1  // τέλος statements_sequence, όχι ερωτηματικό
    ;


    whilecase
        when a=1 : a:=a+1
        when a=2 : a:=a+2
        when a=3 : {
                        a:=a+1;
                        a:=a+2
                   }
        default:   a:=a+1
    ;

    incase
        when a=1 : a:=a+1
        when a=2 : a:=a+2
        when a=3 : {
                        a:=a+1;
                        a:=a+2
                   }
    ;

    untilcase
        when a=1 : a:=a+1
        when a=2 : a:=a+2
        when a=3 : {
                        a:=a+1;
                        a:=a+2
                   }
        until a>100
    ;

    forcase b=10
        when a=1 : a:=a+1
        when a=2 : a:=a+2
        when a=3 : {
                        a:=a+1;
                        a:=a+2
                   }
}