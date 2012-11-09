##!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# Simon Maurer
# Josafat Piraquive

from ig import Live

## ASM descriptor classes
#########################

# label element (i.e main:)
class ASM_label( object ):
    def __init__( self, name ):
        self.DEBUG_type = "ASM_label"
        self.name = name
    def __str__( self ):
        return self.name + ":"

# text description used for the header
class ASM_text( object ):
    def __init__( self, text ):
        self.DEBUG_type = "ASM_text"
        self.text = text
    def __str__( self ):
        return "        ." + self.text


## ASM operand classes
######################
class ASM_operand( object ):
    def __init__( self, child ):
        self.child = child
    def print_alloc( self ):
        return str( self.child )

# register of X86 (%eax, %ebx, etc...)
class ASM_register( ASM_operand ):
    def __init__( self, name, caller=True, color='white' ):
        super(ASM_register, self).__init__( self ) 
        self.name = name
        self.color = color
        self.caller = caller
    def get_name( self ):
        return self.name
    def get_color( self ):
        return self.color
    def is_caller( self ):
        return self.caller
    def __str__( self ):
        return "%" + self.name

# virtual registers used for pseudo assembly
class ASM_v_register( ASM_operand ):
    def __init__( self, name ):
        super(ASM_v_register, self).__init__( self ) 
        self.name = name
        self.spilled = False
        self.new = False
        self.spilled_name = None
        self.color = None
    def get_name( self ):
        return self.name
    def is_spilled( self ):
        return self.spilled
    def set_spilled( self, spilled ):
        self.spilled = spilled
    def is_new( self ):
        return self.new
    def set_new( self, new_val ):
        self.new = new_val
    def get_spilled_name( self ):
        return self.spilled_name
    def set_spilled_name( self, name ):
        self.spilled_name = name
    def get_color( self ):
        return self.color
    def set_color( self, color ):
        self.color = color
    def print_alloc( self ):
        return str( self.color )
    def __str__( self ):
        return self.name

# object indicating the stack position
class ASM_stack( ASM_operand ):
    def __init__( self, pos, stackptr ):
        super(ASM_stack, self).__init__( self ) 
        self.pos = pos
        self.stackptr = stackptr
    def get_pos( self ):
        return self.pos
    def __str__( self ):
        pos_str = ''
        if self.pos != 0:
            pos_str = str(self.pos)
        return  pos_str + "(" + str(self.stackptr) + ")"

# constant (i.e. $3)
class ASM_immedeate( ASM_operand ):
    def __init__(self, val ):
        super(ASM_immedeate, self).__init__( self ) 
        self.val = val
    def get_val( self ):
        return self.val
    def __str__( self ):
        return '$%d' % self.val


# function names and goto labels
class ASM_name( ASM_operand ):
    def __init__(self, name ):
        super(ASM_name, self).__init__( self ) 
        self.name = name
    def get_name( self ):
        return self.name
    def __str__( self ):
        return self.name


## ASM Instruction classes
##########################

# parent class of all instructions
class ASM_instruction( object ):
    def __init__( self, child ):
        self.DEBUG_type = ""
        self.inst_ident = "        "
        self.r_use = []
        self.r_def = []
        self.r_ignore = []
        self.child = child
    def get_r_use( self ):
        return self.r_use
    def get_r_def( self ):
        return self.r_def
    def get_r_ignore( self ):
        return self.r_ignore
    def set_r_use( self, var ):
        if isinstance( var, ASM_v_register ) or isinstance( var, ASM_register ):
            self.r_use.append( Live( var ) )
    def set_r_def( self, var ):
        if isinstance( var, ASM_v_register ) or isinstance( var, ASM_register ):
            self.r_def.append( Live( var ) )
    def set_r_ignore( self, var ):
        if isinstance( var, ASM_register ):
            self.r_ignore.append( Live( var, True ) )
    def print_alloc( self ):
        return str( self.child )
    def print_debug( self ):
        return self.DEBUG_type

# move 
class ASM_movl( ASM_instruction ):
    def __init__( self, left, right ):
        super(ASM_movl, self).__init__( self )
        self.DEBUG_type = "ASM_movl"
        self.left = left
        self.right = right
        self.set_r_use( left )
        self.set_r_def( right )
    def print_alloc( self ):
        return self.inst_ident + "movl " + self.left.print_alloc() + ", " + self.right.print_alloc()
    def __str__( self ):
        return self.inst_ident + "movl " + str(self.left) + ", " + str(self.right)

# push
class ASM_pushl( ASM_instruction ):
    def __init__( self, op ):
        super(ASM_pushl, self).__init__( self )
        self.DEBUG_type = "ASM_pushl"
        self.op = op
    def print_alloc( self ):
        return self.inst_ident + "pushl " + self.op.print_alloc()
    def __str__( self ):
        return self.inst_ident + "pushl " + str(self.op)

# add 
class ASM_addl( ASM_instruction ):
    def __init__( self, left, right ):
        super(ASM_addl, self).__init__( self )
        self.DEBUG_type = "ASM_addl"
        self.left = left
        self.right = right
        self.set_r_def( left )
        self.set_r_use( left )
        self.set_r_use( right )
    def print_alloc( self ):
        return self.inst_ident + "addl " + self.left.print_alloc() + ", " + self.right.print_alloc()
    def __str__( self ):
        return self.inst_ident + "addl " + str(self.left) + ", " + str(self.right)

# subtract
class ASM_subl( ASM_instruction ):
    def __init__( self, left, right ):
        super(ASM_subl, self).__init__( self )
        self.DEBUG_type = "ASM_subl"
        self.left = left
        self.right = right
        self.set_r_def( left )
        self.set_r_use( left )
        self.set_r_use( right )
    def print_alloc( self ):
        return self.inst_ident + "subl " + self.left.print_alloc() + ", " + self.right.print_alloc()
    def __str__( self ):
        return self.inst_ident + "subl " + str(self.left) + ", " + str(self.right)

# unary sub
class ASM_negl( ASM_instruction ):
    def __init__( self, op ):
        super(ASM_negl, self).__init__( self )
        self.DEBUG_type = "ASM_negl"
        self.op = op
        self.set_r_def( op )
        self.set_r_use( op )
    def print_alloc( self ):
        return self.inst_ident + "negl " + self.op.print_alloc()
    def __str__( self ):
        return self.inst_ident + "negl " + str(self.op)

# bitand
class ASM_andl( ASM_instruction ):
    def __init__( self, left, right ):
        super(ASM_andl, self).__init__( self )
        self.DEBUG_type = "ASM_andl"
        self.left = left
        self.right = right
        self.set_r_def( left )
        self.set_r_use( left )
        self.set_r_use( right )
    def print_alloc( self ):
        return self.inst_ident + "andl " + self.left.print_alloc() + ", " + self.right.print_alloc()
    def __str__( self ):
        return self.inst_ident + "andl " + str(self.left) + ", " + str(self.right)

# bitor
class ASM_orl( ASM_instruction ):
    def __init__( self, left, right ):
        super(ASM_orl, self).__init__( self )
        self.DEBUG_type = "ASM_orl"
        self.left = left
        self.right = right
        self.set_r_def( left )
        self.set_r_use( left )
        self.set_r_use( right )
    def print_alloc( self ):
        return self.inst_ident + "orl " + self.left.print_alloc() + ", " + self.right.print_alloc()
    def __str__( self ):
        return self.inst_ident + "orl " + str(self.left) + ", " + str(self.right)

# bitxor
class ASM_xorl( ASM_instruction ):
    def __init__( self, left, right ):
        super(ASM_xorl, self).__init__( self )
        self.DEBUG_type = "ASM_xorl"
        self.left = left
        self.right = right
        self.set_r_def( left )
        self.set_r_use( left )
        self.set_r_use( right )
    def print_alloc( self ):
        return self.inst_ident + "xorl " + self.left.print_alloc() + ", " + self.right.print_alloc()
    def __str__( self ):
        return self.inst_ident + "xorl " + str(self.left) + ", " + str(self.right)

# bitinvert
class ASM_notl( ASM_instruction ):
    def __init__( self, op ):
        super(ASM_notl, self).__init__( self )
        self.DEBUG_type = "ASM_notl"
        self.op = op
        self.set_r_def( op )
        self.set_r_use( op )
    def print_alloc( self ):
        return self.inst_ident + "notl " + self.op.print_alloc()
    def __str__( self ):
        return self.inst_ident + "notl " + str(self.op)

# multiplication
class ASM_imull( ASM_instruction ):
    def __init__( self, left, right ):
        super(ASM_imull, self).__init__( self )
        self.DEBUG_type = "ASM_imull"
        self.left = left
        self.right = right
        self.set_r_def( left )
        self.set_r_use( left )
        self.set_r_use( right )
    def print_alloc( self ):
        return self.inst_ident + "imull " + self.left.print_alloc() + ", " + self.right.print_alloc()
    def __str__( self ):
        return self.inst_ident + "imull " + str(self.left) + ", " + str(self.right)

# function call
class ASM_call( ASM_instruction ):
    def __init__( self, name ):
        super(ASM_call, self).__init__( self )
        self.DEBUG_type = "ASM_call"
        self.name = name
    def __str__( self ):
        return self.inst_ident + "call " + str(self.name)

# return
class ASM_ret( ASM_instruction ):
    def __init__( self ):
        super(ASM_ret, self).__init__( self )
        self.DEBUG_type = "ASM_ret"
    def __str__( self ):
        return self.inst_ident + "ret"

# leave
class ASM_leave( ASM_instruction ):
    def __init__( self ):
        super(ASM_leave, self).__init__( self )
        self.DEBUG_type = "ASM_leave"
    def __str__( self ):
        return self.inst_ident + "leave"

# shift left
class ASM_shll( ASM_instruction ):
    def __init__( self, left, right ):
        super(ASM_shll, self).__init__( self )
        self.DEBUG_type = "ASM_shll"
        self.left = left
        self.right = right
        self.set_r_def( left )
        self.set_r_use( left )
        self.set_r_use( right )
    def print_alloc( self ):
        return self.inst_ident + "shll " + self.left.print_alloc() + ", " + self.right.print_alloc()
    def __str__( self ):
        return self.inst_ident + "shll " + str(self.left) + ", " + str(self.right)

# shift right
class ASM_shrl( ASM_instruction ):
    def __init__( self, left, right ):
        super(ASM_shrl, self).__init__( self )
        self.DEBUG_type = "ASM_shrl"
        self.left = left
        self.right = right
        self.set_r_def( left )
        self.set_r_use( left )
        self.set_r_use( right )
    def print_alloc( self ):
        return self.inst_ident + "shrl " + self.left.print_alloc() + ", " + self.right.print_alloc()
    def __str__( self ):
        return self.inst_ident + "shrl " + str(self.left) + ", " + str(self.right)


