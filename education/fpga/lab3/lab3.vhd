library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity LB3 is
    Port ( clk  : in STD_ULOGIC;                    -- regulate timing
           a, b : in UNSIGNED(3 downto 0);          -- main inputs
           s    : in STD_LOGIC_VECTOR(2 downto 0);  -- select lines
           f    : out UNSIGNED(7 downto 0));        -- main output
end LB3;

architecture Behavioral of LB3 is

begin

    -- main ALU process
    ALU: PROCESS(a, b, s)  -- triggers when a, b, or s changes
        BEGIN
        
            -- conditional to only run if at rising edge of clock
            -- also checking for 1 for the test bench
            --if(rising_edge(clk) OR (clk = '1')) then
            
                -- re-initialize f
                f <= x"00";
                            
                -- case for ALU op selection
                case s is
                    when "000" =>   -- add op (5-bit out)
                        f <= ("0000" & a) + ("0000" & b);
                    when "001" =>   -- sub op
                        f <= ("0000" & a) - ("0000" & b);
                    when "010" =>   -- mul op
                        f <= a * b;
                    when "011" =>   -- div op
                        f <= ("0000" & a) / ("0000" & b);
                    when "100" =>   -- xor op
                        f(3 downto 0) <= ((NOT a AND b) OR (a AND NOT b));
                    when "101" =>   -- = op
                        if (a=b) then
                            f(0) <= '1';
                        else
                            f(0) <= '0';
                        end if;
                    when "110" =>   -- > op
                        if (a>b) then
                            f(1) <= '1';
                        else
                            f(1) <= '0';
                        end if;
                    when "111" =>   -- < op
                        if (a<b) then
                            f(2) <= '1';
                        else
                            f(2) <= '0';
                        end if;
                    when others =>
                        -- code
                end case;
                
            --end if;
            
    END PROCESS;

end Behavioral;
