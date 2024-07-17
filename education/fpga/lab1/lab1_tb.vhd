library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.numeric_std.all;
LIBRARY UNISIM;
USE UNISIM.Vcomponents.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity LB1_tb is
--  Port ( );
end LB1_tb;

architecture Behavioral of LB1_tb is

    COMPONENT LB1
    PORT(a, b, c, d     :   IN      STD_LOGIC;
                  f     :   OUT     STD_LOGIC);
    END COMPONENT;
    
    SIGNAL a, b, c, d, f    : STD_LOGIC;

begin

    UUT: LB1 PORT MAP(
                        a => a,
                        b => b,
                        c => c,
                        d => d,
                        f => f);
                        
    --*** Test Bench - User Defined Section ***
    tb: PROCESS
    BEGIN
                a <= '0'; b <= '0'; c <= '0'; d <= '0';
                wait for 10 ms;
                a <= '0'; b <= '0'; c <= '0'; d <= '1';
                wait for 10 ms;
                a <= '0'; b <= '0'; c <= '1'; d <= '0';
                wait for 10 ms;
                a <= '0'; b <= '0'; c <= '1'; d <= '1';
                wait for 10 ms;
                a <= '0'; b <= '1'; c <= '0'; d <= '0';
                wait for 10 ms;
                a <= '0'; b <= '1'; c <= '0'; d <= '1';
                wait for 10 ms;
                a <= '0'; b <= '1'; c <= '1'; d <= '0';
                wait for 10 ms;
                a <= '0'; b <= '1'; c <= '1'; d <= '1';
                wait for 10 ms;
                a <= '1'; b <= '0'; c <= '0'; d <= '0';
                wait for 10 ms;
                a <= '1'; b <= '0'; c <= '0'; d <= '1';
                wait for 10 ms;
                a <= '1'; b <= '0'; c <= '1'; d <= '0';
                wait for 10 ms;
                a <= '1'; b <= '0'; c <= '1'; d <= '1';
                wait for 10 ms;
                a <= '1'; b <= '1'; c <= '0'; d <= '0';
                wait for 10 ms;
                a <= '1'; b <= '1'; c <= '0'; d <= '1';
                wait for 10 ms;
                a <= '1'; b <= '1'; c <= '1'; d <= '0';
                wait for 10 ms;
                a <= '1'; b <= '1'; c <= '1'; d <= '1';
                wait for 10 ms;
                
    WAIT;--will wait forever
    
    END PROCESS;
--*** End Test Bench - User Defined Section ***

end Behavioral;
