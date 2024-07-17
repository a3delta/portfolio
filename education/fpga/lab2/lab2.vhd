
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

entity LB2 is
    Port ( a : in STD_LOGIC;
           b : in STD_LOGIC;
           c : in STD_LOGIC;
           d : in STD_LOGIC;
           f : out STD_LOGIC);
end LB2;

architecture Structural of LB2 is

    SIGNAL n1, n2, n3           :   STD_LOGIC;
    SIGNAL a1, a2, a3, a4, a5   :   STD_LOGIC;
    SIGNAL o1, o2, o3           :   STD_LOGIC;

    COMPONENT AND_block
        PORT(x, y   : IN    STD_LOGIC;
             g      : OUT   STD_LOGIC);
    END COMPONENT;
    
    COMPONENT OR_block
        PORT(x, y   : IN    STD_LOGIC;
             g      : OUT   STD_LOGIC);
    END COMPONENT;
    
    COMPONENT NOT_block
        PORT(x      : IN    STD_LOGIC;
             g      : OUT   STD_LOGIC);
    END COMPONENT;

begin

    -- F(a, b, c, d) = a'b'd + ac + bc' + c'd
    
    -- invert for NOTs
    not1: NOT_block PORT MAP(x => a, g => n1);
    not2: NOT_block PORT MAP(x => b, g => n2);
    not3: NOT_block PORT MAP(x => c, g => n3);
    
    -- and1-2: a'b'd
    and1: AND_block PORT MAP(x => n1, y => n2, g => a1);
    and2: AND_block PORT MAP(x => a1, y => d, g => a2);
    -- and3: ac
    and3: AND_block PORT MAP(x => a, y => c, g => a3);
    -- or1: and1-2 OR and3
    or1: OR_block PORT MAP(x => a2, y => a3, g => o1);
    
    -- and4: bc'
    and4: AND_block PORT MAP(x => b, y => n3, g => a4);
    -- and5: c'd
    and5: AND_block PORT MAP(x => n3, y => d, g => a5);
    -- or2: and4 OR and5
    or2: OR_block PORT MAP(x => a4, y => a5, g => o2);
    
    -- or3: or1 OR or2
    or3: OR_block PORT MAP(x => o1, y => o2, g => f);
    
end Structural;
