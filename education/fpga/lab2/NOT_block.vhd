
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

entity NOT_block is
    Port ( x : in STD_LOGIC;
           g : out STD_LOGIC);
end NOT_block;

architecture DataFlow of NOT_block is

begin

    g <= NOT x;

end DataFlow;
