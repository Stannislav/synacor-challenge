; r7.asm - doing the 8th register check
; for some reason this program only works for low values
; of r0=eax and r1=ebx.
; need to investigate
; credit to http://peter.michaux.ca/articles/assembly-hello-world-for-os-x
    
section .text

global check                ; make the main function externally visible

check:
    mov eax, 3
    mov ebx, 1
    mov ecx, 7
    call m6027
    call myexit

m6027:
    cmp eax, 0
    jne m6035
    mov eax, ebx
    inc eax
    ret

m6035:
    cmp ebx, 0
    jne m6048
    dec eax
    mov ebx, ecx
    call m6027
    ret

m6048:
    push eax
    dec ebx
    call m6027
    mov ebx, eax
    pop eax
    dec eax
    call m6027
    ret

; a procedure wrapping the system call to exit
myexit:
    push dword eax            ; program will return value in eax
    mov eax, 0x1              ; system call exit code
    sub esp, 4                ; OS X (and BSD) system calls needs "extra space" on stack
    int 0x80                  ; make system call
