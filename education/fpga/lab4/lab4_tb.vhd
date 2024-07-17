library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity LB4_tb is
--  Port ( );
end LB4_tb;

architecture Behavioral of LB4_tb is

    -- component for testing
    COMPONENT LB4
        PORT(clk    : IN STD_LOGIC;
             n      : IN UNSIGNED(1 downto 0);
             reset  : IN STD_LOGIC;
             f      : OUT UNSIGNED(3 downto 0));
    END COMPONENT;

    -- signals to test
    SIGNAL clk      : STD_LOGIC             := '0';
    SIGNAL n        : UNSIGNED(1 downto 0);
    SIGNAL reset    : STD_LOGIC             := '1';
    SIGNAL f        : UNSIGNED(3 downto 0)  := "0000";

begin

    UUT: LB4 PORT MAP(clk=>clk, n=>n, reset=>reset, f=>f);
    
    -- test bench process
    tb: PROCESS
    BEGIN
    
        -- set n = 3
        n <= "11";
        
        -- trigger state A
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state B
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state C
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state A (n = 3, natural reset)
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state B
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger single reset to test
        reset <= '0';       -- press reset
        
        -- trigger state A (reset = 0)
        clk <= '1';
        wait for 5 ms;
        reset <= '1';       -- release reset
        clk <= '0';
        wait for 5 ms;
        
        -- set n = 2
        n <= "10";
        
        -- trigger state A (changed n)
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state B
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state C
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state D
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state A (n = 2, natural reset)
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- set n = 1
        n <= "01";
        
        -- trigger state A (changed n)
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state B
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state C
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state D
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state E
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state F
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state G
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state H
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state I
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state A (n = 1, natural reset)
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- set n = 0
        n <= "00";
        
        -- trigger state A (changed n)
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state B
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state C
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state D
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state E
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state F
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state G
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state H
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state I
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state J
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state K
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state L
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state M
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state N
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state O
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state P
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state Q
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- trigger state A (n = 0, natural reset)
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
    
    WAIT;
    
    END PROCESS;
    -- end test bench

end Behavioral;
