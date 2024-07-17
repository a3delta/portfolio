library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity LB3_tb is
--  Port ( );
end LB3_tb;

architecture Behavioral of LB3_tb is

    -- component for testing
    COMPONENT LB3
        PORT(clk    : IN STD_ULOGIC;
             a, b   : IN UNSIGNED(3 downto 0);
             s      : IN STD_LOGIC_VECTOR(2 downto 0);
             f      : OUT UNSIGNED(7 downto 0));
    END COMPONENT;

    -- signals to test
    SIGNAL clk      : STD_ULOGIC                    := '1';
    SIGNAL a, b     : UNSIGNED(3 downto 0)  := "0000";
    SIGNAL s        : STD_LOGIC_VECTOR(2 downto 0)  := "000";
    SIGNAL f        : UNSIGNED(7 downto 0)  := "00000000";

begin

    UUT: LB3 PORT MAP(clk=>clk, a=>a, b=>b, s=>s, f=>f);
    
    -- test bench process
    tb: PROCESS
    BEGIN
    
        -- set input values
        a <= "1100"; b <= "1001";
    
        -- add op
        s <= "000";
        wait for 10 ms;
        
        -- sub op
        s <= "001";
        wait for 10 ms;
        
        -- mul op
        s <= "010";
        wait for 10 ms;
        
        -- div op
        s <= "011";
        wait for 10 ms;
        
        -- xor op
        s <= "100";
        wait for 10 ms;
        
        -- = op - !=
        a <= "1100"; b <= "1001";
        s <= "101";
        wait for 10 ms;
        
        -- = op - ==
        a <= "1001"; b <= "1001";
        s <= "101";
        wait for 10 ms;
        
        -- > op - a > b
        a <= "1100"; b <= "1001";
        s <= "110";
        wait for 10 ms;
        
        -- > op - a <= b
        a <= "1001"; b <= "1100";
        s <= "110";
        wait for 10 ms;
        
        -- < op - a < b
        a <= "1001"; b <= "1100";
        s <= "111";
        wait for 10 ms;
        
        -- < op - a >= b
        a <= "1100"; b <= "1001";
        s <= "111";
        wait for 10 ms;
    
    WAIT;
    
    END PROCESS;
    -- end test bench

end Behavioral;
