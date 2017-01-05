nasm -f macho r7.asm
ld -o r7 -e check r7.o
./r7
echo $?