ENTRY(hook)
SECTIONS {
  . = 0x0203F768;
  .text : { *(.entry) *(.text*) *(.rodata*) }
  . = ALIGN(4);
  .config : { *(.config) }
  .state : { *(.state) }
  .data : { *(.data*) *(.bss*) *(COMMON) }
  . = ALIGN(4);
  end = .;
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.ARM.attributes) }
  ASSERT(end <= 0x02040000, "resident exceeds verified EWRAM reservation")
}
