set disassembly-flavor intel
echo ------------------------------
r test.sample
where
i r
x/10i $rip
echo ------------------------------
