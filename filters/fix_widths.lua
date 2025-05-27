-- Rescale Pandoc-generated column widths so they never exceed the page.
-- Works with Pandoc ≥ 3 (ColWidth table) and older numeric format.

local max_total = 0.98   -- leave 2 % breathing space for tabcolsep, rules…

local function get_width(col)
  local w = col[2]
  if type(w) == "table" and w[1] == "ColWidth" then return w[2] end
  if type(w) == "number"                     then return w    end
  return 0
end

local function set_width(col, w)
  if type(col[2]) == "table" then
    col[2] = {"ColWidth", w}
  else
    col[2] = w
  end
end

function Table(tbl)
  -- total relative width assigned by Pandoc
  local total = 0
  for _,col in ipairs(tbl.colspecs) do total = total + get_width(col) end
  if total > 0 and total > max_total then
    local factor = max_total / total
    for _,col in ipairs(tbl.colspecs) do
      set_width(col, get_width(col) * factor)
    end
  end
  return tbl
end
