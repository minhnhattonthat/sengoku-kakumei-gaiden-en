-- Proves --script probes run: logs one line at frame 60.
L.on_frame(function(n)
  if n == 60 then L.log("probe ok frame " .. n) end
end)
