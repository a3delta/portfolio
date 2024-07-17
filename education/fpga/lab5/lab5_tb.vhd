library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity LB5_tb is
--  Port ( );
end LB5_tb;

architecture Behavioral of LB5_tb is

    -- component for testing
    COMPONENT LB5
        PORT(clk    : IN  STD_LOGIC;
             w      : IN  STD_LOGIC;
             seq    : IN  STD_LOGIC_VECTOR(3 downto 0);
             reset  : IN  STD_LOGIC;
             z      : OUT STD_LOGIC);
    END COMPONENT;
    
    -- signals to test
    SIGNAL clk      : STD_LOGIC := '0';
    SIGNAL w        : STD_LOGIC := '0';
    SIGNAL seq      : STD_LOGIC_VECTOR(3 downto 0) := "0000";
    SIGNAL reset    : STD_LOGIC := '1';
    SIGNAL z        : STD_LOGIC;

begin
    
    -- map ports
    UUT: LB5 PORT MAP(clk=>clk, w=>w, seq=>seq, reset=>reset, z=>z);
    
    -- test bench process
    tb: PROCESS
    BEGIN

        -- set seq = 1010
        seq <= "1010";
        
        -- z = 1 test: state change A to B
        w <= '1';
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- z = 1 test: state change B to C
        w <= '0';
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- z = 1 test: state change C to D
        w <= '1';
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- z = 1 test: state change D to A
        w <= '0';
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- z = 0 test: state change A to B
        w <= '1';
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- z = 0 test: state change B to C
        w <= '0';
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- z = 0 test: state change C to A
        w <= '0';
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- z = 0 test: state change A to B
        w <= '1';
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- set seq = 1101
        seq <= "1101";
                
        -- z = 1 overlap test: state change B to C
        w <= '1';
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- z = 1 overlap test: state change C to D
        w <= '0';
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- z = 1 overlap test: state change D to B
        w <= '1';
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
               
        -- z = 0 test: state change B to C
        w <= '1';
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- z = 0 test: state change C to B
        w <= '1';
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- z = 0 test: state change B to B
        w <= '1';
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- seq = 1001
        seq <= "1001";
        
        -- reset test: back to state A and z = 0
        reset <= '0';
        clk <= '1';
        wait for 5 ms;
        reset <= '1';
        clk <= '0';
        wait for 5 ms;
        
        -- reset test: state change A to B
        w <= '1';
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- reset test: state change B to C
        w <= '0';
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- reset test: state change C to D
        w <= '0';
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
        -- reset test: state change D to B
        w <= '1';
        clk <= '1';
        wait for 5 ms;
        clk <= '0';
        wait for 5 ms;
        
    WAIT;

    END PROCESS;
    -- end test bench

end Behavioral;
