import sys
from typing import List, Optional, TextIO, Any, Union
import enum

# Imports from previous files
from ast_node import (
    ASTNode, ASTNodeType, ASTBlock, ASTBinary, ASTTernary, ASTUnary,
    ASTCall, ASTDelete, ASTExec, ASTFormattedValue, ASTJoinedStr,
    ASTKeyword, ASTList, ASTSet, ASTComprehension, ASTMap, ASTConstMap,
    ASTName, ASTNodeList, ASTPrint, ASTRaise, ASTReturn, ASTSlice,
    ASTImport, ASTFunction, ASTStore, ASTChainStore, ASTSubscr, ASTConvert,
    ASTAnnotatedVar, ASTClass, ASTIterBlock, ASTCondBlock, ASTWithBlock, ASTObject,
    ASTTuple, ASTLoadBuildClass, ASTKwNamesMap
)
from bytecode import Opcode, bc_next
from fast_stack import FastStack
from pyc_code import PycCode
from pyc_module import PycModule
from pyc_object import PycObject, PycObjectType
from pyc_string import PycString
from pyc_sequence import PycTuple
from data import PycBuffer

# Global state variables (mirroring static vars in C++)
clean_build = True
in_lambda = False
print_docstring_and_globals = False
print_class_docstring = True
cur_indent = -1
F_STRING_QUOTE = "'''"

def stack_pop_top(stack: FastStack) -> Optional[ASTNode]:
    node = stack.top()
    stack.pop()
    return node

def get_name_bytes(n: ASTNode) -> Optional[bytes]:
    if n is None: return None
    t = getattr(n, 'type', None)
    if t == ASTNodeType.NODE_NAME:
        return n.name.value if hasattr(n.name, 'value') else n.name
    elif t == ASTNodeType.NODE_IMPORT:
        if hasattr(n, 'name') and getattr(n.name, 'type', None) == ASTNodeType.NODE_NAME:
            return n.name.name.value if hasattr(n.name.name, 'value') else n.name.name
    return None

def is_equal_name(node1: ASTNode, node2: ASTNode) -> bool:
    name1 = get_name_bytes(node1)
    name2 = get_name_bytes(node2)
    return name1 is not None and name2 is not None and name1 == name2

def check_if_expr(stack: FastStack, curblock: ASTBlock):
    if stack.empty():
        return
    if len(curblock.nodes) < 2:
        return

    # Check for "else" block at the end
    last_node = curblock.nodes[-1]
    if last_node.type != ASTNodeType.NODE_BLOCK:
        return
    if not isinstance(last_node, ASTBlock) or last_node.blktype != ASTBlock.BlkType.BLK_ELSE:
        return
    
    # Check for "if" block before it
    prev_node = curblock.nodes[-2]
    if prev_node.type != ASTNodeType.NODE_BLOCK:
        return
    if not isinstance(prev_node, ASTBlock) or prev_node.blktype != ASTBlock.BlkType.BLK_IF:
        return

    # Convert to Ternary
    else_expr = stack_pop_top(stack)
    curblock.remove_last() # Remove else block
    
    if_block = curblock.nodes[-1] # This is the if block node
    
    if_expr = stack_pop_top(stack)
    curblock.remove_last() # Remove if block
    
    stack.push(ASTTernary(if_block, if_expr, else_expr))

def append_to_chain_store(chain_store: ASTNode, item: ASTNode, stack: FastStack, curblock: ASTBlock):
    stack.pop() # ignore identical source object
    if hasattr(chain_store, 'append'):
        chain_store.append(item)
    
    top_node = stack.top()
    is_null = False
    if top_node is not None and getattr(top_node, 'type', None) == ASTNodeType.NODE_OBJECT:
        if getattr(top_node.object, 'type', None) == getattr(PycObjectType, 'TYPE_NULL', None):
            is_null = True
            
    if is_null:
        curblock.append(chain_store)
    else:
        stack.push(chain_store)

def build_from_code(code: PycCode, mod: PycModule) -> ASTNode:
    global clean_build
    
    code_bytes = code.code.value
    source = PycBuffer(code_bytes)

    stack_size = 20 if mod.major_ver == 1 else code.stackSize
    stack = FastStack(stack_size)
    stack_hist: List[FastStack] = []

    blocks: List[ASTBlock] = []
    defblock = ASTBlock(ASTBlock.BlkType.BLK_MAIN)
    defblock.init()
    curblock = defblock
    blocks.append(defblock)

    opcode = 0
    operand = 0
    pos = 0
    unpack = 0
    else_pop = False
    need_try = False
    variable_annotations = False
    
    while not source.at_eof():
        curpos = pos
        opcode_val, operand, pos_inc = bc_next(source, mod)
        opcode = Opcode(opcode_val) 
        pos += pos_inc

        if need_try and opcode != Opcode.SETUP_EXCEPT_A:
            need_try = False
            stack_hist.append(stack.copy())
            tryblock = ASTBlock(ASTBlock.BlkType.BLK_TRY, curblock.end, 1)
            blocks.append(tryblock)
            curblock = tryblock
        elif else_pop and opcode not in (
            Opcode.JUMP_FORWARD_A, Opcode.JUMP_IF_FALSE_A, Opcode.JUMP_IF_FALSE_OR_POP_A,
            Opcode.POP_JUMP_IF_FALSE_A, Opcode.POP_JUMP_FORWARD_IF_FALSE_A,
            Opcode.JUMP_IF_TRUE_A, Opcode.JUMP_IF_TRUE_OR_POP_A,
            Opcode.POP_JUMP_IF_TRUE_A, Opcode.POP_JUMP_FORWARD_IF_TRUE_A,
            Opcode.POP_BLOCK
        ):
            else_pop = False
            while len(blocks) > 0:
                prev = curblock
                if prev.end < pos and prev.blktype != ASTBlock.BlkType.BLK_MAIN:
                    if prev.blktype != ASTBlock.BlkType.BLK_CONTAINER:
                        if prev.end == 0:
                            break
                        if stack_hist:
                            stack_hist.pop()
                    
                    blocks.pop()
                    if not blocks:
                        break
                        
                    curblock = blocks[-1]
                    curblock.append(prev)
                    check_if_expr(stack, curblock)
                else:
                    break

        if opcode == Opcode.BINARY_OP_A:
            is_inplace = (operand >= 13)
            op = ASTBinary.from_binary_op(operand)
            right = stack_pop_top(stack)
            left = stack_pop_top(stack)
            
            if left is None: left = ASTName(PycString(None, b"underflow"))
            if right is None: right = ASTName(PycString(None, b"underflow"))
            
            bin_node = ASTBinary(left, right, op)
            bin_node.inplace = is_inplace
            stack.push(bin_node)

        elif opcode in (
            Opcode.BINARY_ADD, Opcode.BINARY_AND, Opcode.BINARY_DIVIDE,
            Opcode.BINARY_FLOOR_DIVIDE, Opcode.BINARY_LSHIFT, Opcode.BINARY_MODULO,
            Opcode.BINARY_MULTIPLY, Opcode.BINARY_OR, Opcode.BINARY_POWER,
            Opcode.BINARY_RSHIFT, Opcode.BINARY_SUBTRACT, Opcode.BINARY_TRUE_DIVIDE,
            Opcode.BINARY_XOR, Opcode.BINARY_MATRIX_MULTIPLY,
            Opcode.INPLACE_ADD, Opcode.INPLACE_AND, Opcode.INPLACE_DIVIDE,
            Opcode.INPLACE_FLOOR_DIVIDE, Opcode.INPLACE_LSHIFT, Opcode.INPLACE_MODULO,
            Opcode.INPLACE_MULTIPLY, Opcode.INPLACE_OR, Opcode.INPLACE_POWER,
            Opcode.INPLACE_RSHIFT, Opcode.INPLACE_SUBTRACT, Opcode.INPLACE_TRUE_DIVIDE,
            Opcode.INPLACE_XOR, Opcode.INPLACE_MATRIX_MULTIPLY
        ):
            op = ASTBinary.from_opcode(opcode)
            if op == ASTBinary.BinOp.BIN_INVALID:
                raise RuntimeError("Unhandled opcode from ASTBinary::from_opcode")
            right = stack_pop_top(stack)
            left = stack_pop_top(stack)
            stack.push(ASTBinary(left, right, op))

        elif opcode == Opcode.BINARY_SUBSCR:
            subscr = stack_pop_top(stack)
            src = stack_pop_top(stack)
            stack.push(ASTSubscr(src, subscr))

        elif opcode == Opcode.BREAK_LOOP:
            curblock.append(ASTKeyword(ASTKeyword.Word.KW_BREAK))

        elif opcode == Opcode.BUILD_CLASS:
            class_code = stack_pop_top(stack)
            bases = stack_pop_top(stack)
            name = stack_pop_top(stack)
            stack.push(ASTClass(class_code, bases, name))

        elif opcode == Opcode.BUILD_FUNCTION:
            fun_code = stack_pop_top(stack)
            stack.push(ASTFunction(fun_code, [], []))

        elif opcode == Opcode.BUILD_LIST_A:
            values = []
            for _ in range(operand):
                values.insert(0, stack_pop_top(stack))
            stack.push(ASTList(values))

        elif opcode == Opcode.BUILD_SET_A:
            values = []
            for _ in range(operand):
                values.insert(0, stack_pop_top(stack))
            stack.push(ASTSet(values))

        elif opcode == Opcode.BUILD_MAP_A:
            if mod.ver_compare(3, 5) >= 0:
                map_node = ASTMap()
                items = []
                for _ in range(operand):
                    val = stack_pop_top(stack)
                    key = stack_pop_top(stack)
                    items.insert(0, (key, val))
                
                for key, val in items:
                    map_node.add(key, val)
                
                stack.push(map_node)
            else:
                if stack.top() and stack.top().type == ASTNodeType.NODE_CHAINSTORE:
                    stack.pop()
                stack.push(ASTMap())

        elif opcode == Opcode.BUILD_CONST_KEY_MAP_A:
            keys_node = stack_pop_top(stack)
            values = []
            for _ in range(operand):
                values.insert(0, stack_pop_top(stack))
            stack.push(ASTConstMap(keys_node, values))

        elif opcode == Opcode.STORE_MAP:
            key = stack_pop_top(stack)
            value = stack_pop_top(stack)
            map_node = stack.top()
            if isinstance(map_node, ASTMap):
                map_node.add(key, value)

        elif opcode == Opcode.BUILD_SLICE_A:
            def is_none(node):
                return (node is None or 
                       (getattr(node, 'type', None) == ASTNodeType.NODE_OBJECT and 
                        getattr(node.object, 'type', None) == PycObjectType.TYPE_NONE))

            if operand == 2:
                end = stack_pop_top(stack)
                start = stack_pop_top(stack)
                if is_none(start): start = None
                if is_none(end): end = None
                
                if start is None and end is None:
                    stack.push(ASTSlice(ASTSlice.SliceOp.SLICE0))
                elif start is None:
                    stack.push(ASTSlice(ASTSlice.SliceOp.SLICE2, start, end))
                elif end is None:
                    stack.push(ASTSlice(ASTSlice.SliceOp.SLICE1, start, end))
                else:
                    stack.push(ASTSlice(ASTSlice.SliceOp.SLICE3, start, end))
                    
            elif operand == 3:
                step = stack_pop_top(stack)
                end = stack_pop_top(stack)
                start = stack_pop_top(stack)
                if is_none(start): start = None
                if is_none(end): end = None
                if is_none(step): step = None
                
                lhs = None
                if start is None and end is None:
                    lhs = ASTSlice(ASTSlice.SliceOp.SLICE0)
                elif start is None:
                    lhs = ASTSlice(ASTSlice.SliceOp.SLICE2, start, end)
                elif end is None:
                    lhs = ASTSlice(ASTSlice.SliceOp.SLICE1, start, end)
                else:
                    lhs = ASTSlice(ASTSlice.SliceOp.SLICE3, start, end)
                
                if step is None:
                    stack.push(ASTSlice(ASTSlice.SliceOp.SLICE1, lhs, step))
                else:
                    stack.push(ASTSlice(ASTSlice.SliceOp.SLICE3, lhs, step))

        elif opcode == Opcode.BUILD_STRING_A:
            values = []
            for _ in range(operand):
                values.insert(0, stack_pop_top(stack))
            stack.push(ASTJoinedStr(values))

        elif opcode == Opcode.BUILD_TUPLE_A:
            tos = stack.top()
            if tos and getattr(tos, 'type', None) == getattr(ASTNodeType, 'NODE_LOADBUILDCLASS', 999):
                pass
            else:
                values = []
                for _ in range(operand):
                    values.insert(0, stack_pop_top(stack))
                stack.push(ASTTuple(values))

        elif opcode == Opcode.KW_NAMES_A:
            const_tuple = code.getConst(operand) 
            kw_count = len(const_tuple.values)
            keys = const_tuple.values
            
            kw_items = []
            for i in range(kw_count):
                key = ASTObject(keys[kw_count - i - 1])
                val = stack_pop_top(stack)
                kw_items.append((key, val))
            
            if hasattr(sys.modules[__name__], 'ASTKwNamesMap'):
                kw_map = ASTKwNamesMap()
            else:
                kw_map = ASTMap()
            
            for k, v in kw_items:
                kw_map.add(k, v)
                
            stack.push(kw_map)

        elif opcode in (Opcode.CALL_A, Opcode.CALL_FUNCTION_A, getattr(Opcode, 'INSTRUMENTED_CALL_A', None)):
            kwparams = (operand & 0xFF00) >> 8
            pparams = (operand & 0xFF)
            kwparamList = []
            pparamList = []

            stack_hist.append(stack.copy())
            basecnt = 0
            bases = []
            
            TOS = stack.top()
            TOS_type = getattr(TOS, 'type', None) if TOS else None
            while TOS_type in (ASTNodeType.NODE_NAME, ASTNodeType.NODE_BINARY):
                bases.append(TOS)
                basecnt += 1
                stack.pop()
                TOS = stack.top()
                TOS_type = getattr(TOS, 'type', None) if TOS else None
            
            name = stack_pop_top(stack)
            function = stack_pop_top(stack)
            loadbuild = stack_pop_top(stack)
            loadbuild_type = getattr(loadbuild, 'type', None) if loadbuild else None
            
            if loadbuild_type == getattr(ASTNodeType, 'NODE_LOADBUILDCLASS', 999):
                call = ASTCall(function, pparamList, kwparamList)
                stack.push(ASTClass(call, ASTTuple(bases), name))
                stack_hist.pop()
            else:
                stack = stack_hist[-1]
                stack_hist.pop()

                if mod.ver_compare(3, 11) >= 0:
                    object_or_map = stack.top()
                    if object_or_map is not None and getattr(object_or_map, 'type', None) == getattr(ASTNodeType, 'NODE_KW_NAMES_MAP', 999):
                        kw_map_node = stack_pop_top(stack)
                        for key, val in reversed(kw_map_node.values):
                            kwparamList.insert(0, (key, val))
                            pparams -= 1
                
                if not kwparamList and kwparams > 0:
                    for _ in range(kwparams):
                        val = stack_pop_top(stack)
                        key = stack_pop_top(stack)
                        kwparamList.insert(0, (key, val))
                        
                for _ in range(pparams):
                    param = stack_pop_top(stack)
                    if param is not None and getattr(param, 'type', None) == ASTNodeType.NODE_FUNCTION:
                        try:
                            fun_code_node = param.code
                            if getattr(fun_code_node, 'type', None) == ASTNodeType.NODE_OBJECT:
                                code_src = fun_code_node.object
                                if hasattr(code_src, 'name') and code_src.name.value != b"<lambda>":
                                    decor_name = ASTName(code_src.name)
                                    curblock.append(ASTStore(param, decor_name))
                                    pparamList.insert(0, decor_name)
                                else:
                                    pparamList.insert(0, param)
                            else:
                                pparamList.insert(0, param)
                        except:
                            pparamList.insert(0, param)
                    else:
                        pparamList.insert(0, param)
                        
                func = stack_pop_top(stack)
                
                if opcode in (getattr(Opcode, 'CALL_A', None), getattr(Opcode, 'INSTRUMENTED_CALL_A', None)):
                    tos = stack.top()
                    if tos is None or (getattr(tos, 'type', None) == ASTNodeType.NODE_OBJECT and getattr(tos.object, 'type', None) == getattr(PycObjectType, 'TYPE_NONE', None)):
                        stack.pop()
                    else:
                        pparamList.insert(0, tos)
                        stack.pop()

                stack.push(ASTCall(func, pparamList, kwparamList))

        elif opcode == Opcode.CALL_FUNCTION_VAR_A:
            var_arg = stack_pop_top(stack)
            kwparams = (operand & 0xFF00) >> 8
            pparams = (operand & 0xFF)
            kw_args = []
            pos_args = []
            for _ in range(kwparams):
                val = stack_pop_top(stack)
                key = stack_pop_top(stack)
                kw_args.insert(0, (key, val))
            for _ in range(pparams):
                pos_args.insert(0, stack_pop_top(stack))
            func = stack_pop_top(stack)
            call_node = ASTCall(func, pos_args, kw_args)
            call_node.var = var_arg
            stack.push(call_node)

        elif opcode == Opcode.CALL_FUNCTION_KW_A:
            kw_arg = stack_pop_top(stack)
            kwparams = (operand & 0xFF00) >> 8
            pparams = (operand & 0xFF)
            kw_args = []
            pos_args = []
            for _ in range(kwparams):
                val = stack_pop_top(stack)
                key = stack_pop_top(stack)
                kw_args.insert(0, (key, val))
            for _ in range(pparams):
                pos_args.insert(0, stack_pop_top(stack))
            func = stack_pop_top(stack)
            call_node = ASTCall(func, pos_args, kw_args)
            call_node.kw = kw_arg
            stack.push(call_node)

        elif opcode == Opcode.CALL_FUNCTION_VAR_KW_A:
            kw_arg = stack_pop_top(stack)
            var_arg = stack_pop_top(stack)
            kwparams = (operand & 0xFF00) >> 8
            pparams = (operand & 0xFF)
            kw_args = []
            pos_args = []
            for _ in range(kwparams):
                val = stack_pop_top(stack)
                key = stack_pop_top(stack)
                kw_args.insert(0, (key, val))
            for _ in range(pparams):
                pos_args.insert(0, stack_pop_top(stack))
            func = stack_pop_top(stack)
            call_node = ASTCall(func, pos_args, kw_args)
            call_node.var = var_arg
            call_node.kw = kw_arg
            stack.push(call_node)

        elif opcode == Opcode.CALL_METHOD_A:
            pos_args = []
            for _ in range(operand):
                param = stack_pop_top(stack)
                is_decorated = False
                if getattr(param, 'type', None) == ASTNodeType.NODE_FUNCTION:
                    try:
                        fun_code_node = param.code
                        if getattr(fun_code_node, 'type', None) == ASTNodeType.NODE_OBJECT:
                            code_src = fun_code_node.object
                            if hasattr(code_src, 'name') and code_src.name.value != b"<lambda>":
                                decor_name = ASTName(code_src.name)
                                curblock.append(ASTStore(param, decor_name))
                                pos_args.insert(0, decor_name)
                                is_decorated = True
                    except:
                        pass
                if not is_decorated:
                    pos_args.insert(0, param)
            func = stack_pop_top(stack)
            stack.push(ASTCall(func, pos_args, []))

        elif opcode == Opcode.CONTINUE_LOOP_A:
            curblock.append(ASTKeyword(ASTKeyword.Word.KW_CONTINUE))
            
        elif opcode == Opcode.COMPARE_OP_A:
            right = stack_pop_top(stack)
            left = stack_pop_top(stack)
            arg = operand
            if mod.ver_compare(3, 12) == 0:
                arg >>= 4 
            elif mod.ver_compare(3, 13) >= 0:
                arg >>= 5
            cmp_node = ASTBinary(left, right, arg, getattr(ASTNodeType, 'NODE_COMPARE', 999))
            stack.push(cmp_node)

        elif opcode == Opcode.CONTAINS_OP_A:
            right = stack_pop_top(stack)
            left = stack_pop_top(stack)
            op = 7 if operand else 6 
            stack.push(ASTBinary(left, right, op, ASTNodeType.NODE_COMPARE))

        elif opcode == Opcode.DELETE_ATTR_A:
            name = stack_pop_top(stack)
            attr_name = ASTName(code.getName(operand))
            target = ASTBinary(name, attr_name, ASTBinary.BinOp.BIN_ATTR)
            curblock.append(ASTDelete(target))

        elif opcode in (Opcode.DELETE_GLOBAL_A, Opcode.DELETE_NAME_A):
            if opcode == Opcode.DELETE_GLOBAL_A:
                code.markGlobal(code.getName(operand))
            varname = code.getName(operand)
            if len(varname.value) >= 2 and varname.value.startswith(b"_["):
                pass
            else:
                curblock.append(ASTDelete(ASTName(varname)))

        elif opcode == Opcode.DELETE_FAST_A:
            if mod.ver_compare(1, 3) < 0:
                name_obj = code.getName(operand)
            else:
                name_obj = code.getLocal(operand)
            if len(name_obj.value) >= 2 and name_obj.value.startswith(b"_["):
                pass
            else:
                curblock.append(ASTDelete(ASTName(name_obj)))

        elif opcode == Opcode.DELETE_SLICE_0:
            name = stack_pop_top(stack)
            curblock.append(ASTDelete(ASTSubscr(name, ASTSlice(ASTSlice.SliceOp.SLICE0))))

        elif opcode == Opcode.DELETE_SLICE_1:
            upper = stack_pop_top(stack)
            name = stack_pop_top(stack)
            curblock.append(ASTDelete(ASTSubscr(name, ASTSlice(ASTSlice.SliceOp.SLICE1, None, upper))))

        elif opcode == Opcode.DELETE_SLICE_2:
            lower = stack_pop_top(stack)
            name = stack_pop_top(stack)
            curblock.append(ASTDelete(ASTSubscr(name, ASTSlice(ASTSlice.SliceOp.SLICE2, lower, None))))

        elif opcode == Opcode.DELETE_SLICE_3:
            lower = stack_pop_top(stack)
            upper = stack_pop_top(stack)
            name = stack_pop_top(stack)
            curblock.append(ASTDelete(ASTSubscr(name, ASTSlice(ASTSlice.SliceOp.SLICE3, lower, upper))))

        elif opcode == Opcode.DELETE_SUBSCR:
            key = stack_pop_top(stack)
            name = stack_pop_top(stack)
            curblock.append(ASTDelete(ASTSubscr(name, key)))

        elif opcode == Opcode.DUP_TOP:
            top = stack.top()
            is_none = (top is None)
            if not is_none and getattr(top, 'type', None) == ASTNodeType.NODE_OBJECT:
                if getattr(top.object, 'type', None) == getattr(PycObjectType, 'TYPE_NONE', None):
                    is_none = True
            if is_none:
                stack.push(top)
            elif getattr(top, 'type', None) == ASTNodeType.NODE_CHAINSTORE:
                chainstore = stack_pop_top(stack)
                stack.push(stack.top())
                stack.push(chainstore)
            else:
                val = stack.top()
                stack.push(val)
                stack.push(ASTChainStore([], val))

        elif opcode == Opcode.DUP_TOP_TWO:
            first = stack_pop_top(stack)
            second = stack.top()
            stack.push(first)
            stack.push(second)
            stack.push(first)

        elif opcode == Opcode.DUP_TOPX_A:
            first = []
            for _ in range(operand):
                first.append(stack_pop_top(stack))
            first.reverse()
            for node in first:
                stack.push(node)
            for node in first:
                stack.push(node)

        elif opcode == Opcode.END_FINALLY:
            is_finally = False
            if curblock.blktype == ASTBlock.BlkType.BLK_FINALLY:
                final_blk = curblock
                blocks.pop()
                stack = stack_hist.pop()
                curblock = blocks[-1]
                curblock.append(final_blk)
                is_finally = True
            elif curblock.blktype == ASTBlock.BlkType.BLK_EXCEPT:
                blocks.pop()
                prev = curblock
                is_uninit_async_for = False
                if blocks[-1].blktype == ASTBlock.BlkType.BLK_CONTAINER:
                    container = blocks[-1] 
                    blocks.pop()
                    async_for_blk = blocks[-1] 
                    is_uninit_async_for = (async_for_blk.blktype == ASTBlock.BlkType.BLK_ASYNCFOR and not async_for_blk.inited)
                    if is_uninit_async_for:
                        try_blk = container.nodes[0]
                        if try_blk.nodes and try_blk.blktype == ASTBlock.BlkType.BLK_TRY:
                            store = try_blk.nodes[0]
                            if getattr(store, 'type', None) == ASTNodeType.NODE_STORE:
                                async_for_blk.set_index(store.dest)
                        curblock = blocks[-1]
                        stack = stack_hist.pop()
                    else:
                        blocks.append(container) 
                if not is_uninit_async_for:
                    if len(curblock.nodes) != 0:
                        blocks[-1].append(curblock)
                    curblock = blocks[-1]
                    has_finally = getattr(curblock, 'has_finally', False)
                    if curblock.end != pos or has_finally:
                        elseblk = ASTBlock(ASTBlock.BlkType.BLK_ELSE, prev.end)
                        elseblk.init()
                        blocks.append(elseblk)
                        curblock = elseblk
                    else:
                        stack = stack_hist.pop()
            if curblock.blktype == ASTBlock.BlkType.BLK_CONTAINER:
                cont = curblock
                has_finally = getattr(cont, 'has_finally', False)
                if not has_finally or is_finally:
                    blocks.pop()
                    curblock = blocks[-1]
                    curblock.append(cont)

        elif opcode == Opcode.EXEC_STMT:
            if getattr(stack.top(), 'type', None) == ASTNodeType.NODE_CHAINSTORE:
                stack.pop()
            loc = stack_pop_top(stack)
            glob = stack_pop_top(stack)
            stmt = stack_pop_top(stack)
            curblock.append(ASTExec(stmt, glob, loc))

        elif opcode in (Opcode.FOR_ITER_A, getattr(Opcode, 'INSTRUMENTED_FOR_ITER_A', None)):
            iter_node = stack_pop_top(stack)
            end = 0
            comprehension = False
            if mod.major_ver == 3 and mod.minor_ver >= 8:
                end = operand
                if mod.ver_compare(3, 10) >= 0:
                    end *= 2
                end += pos
                if code.name.value == b"<listcomp>":
                    comprehension = True
            else:
                top_blk = blocks[-1]
                end = top_blk.end
                if top_blk.blktype == ASTBlock.BlkType.BLK_WHILE:
                    blocks.pop()
                else:
                    comprehension = True
            forblk = ASTIterBlock(ASTBlock.BlkType.BLK_FOR, curpos, end, iter_node)
            forblk.set_comprehension(comprehension)
            blocks.append(forblk)
            curblock = forblk
            stack.push(None)          

        elif opcode == Opcode.FOR_LOOP_A:
            curidx = stack_pop_top(stack) 
            iter_node = stack_pop_top(stack) 
            comprehension = False
            top = blocks[-1] if blocks else None
            if top and top.blktype == ASTBlock.BlkType.BLK_WHILE:
                blocks.pop()
            else:
                comprehension = True
            end_pos = top.end if top else 0
            forblk = ASTIterBlock(ASTBlock.BlkType.BLK_FOR, curpos, end_pos, iter_node)
            forblk.set_comprehension(comprehension)
            blocks.append(forblk)
            curblock = forblk
            stack.push(iter_node)
            stack.push(curidx)
            stack.push(None) 

        elif opcode == Opcode.GET_AITER:
            iter_node = stack_pop_top(stack)
            top = blocks[-1] if blocks else None
            if top and top.blktype == ASTBlock.BlkType.BLK_WHILE:
                blocks.pop()
                forblk = ASTIterBlock(ASTBlock.BlkType.BLK_ASYNCFOR, curpos, top.end, iter_node)
                blocks.append(forblk)
                curblock = forblk
                stack.push(None)
            else:
                sys.stderr.write("Unsupported use of GET_AITER outside of SETUP_LOOP\n")

        elif opcode == Opcode.GET_ANEXT:
            pass 

        elif opcode == Opcode.FORMAT_VALUE_A:
            conversion_flag = operand
            format_spec = None
            if conversion_flag & ASTFormattedValue.ConversionFlag.HAVE_FMT_SPEC:
                format_spec = stack_pop_top(stack)
            val = stack_pop_top(stack)
            stack.push(ASTFormattedValue(val, conversion_flag, format_spec))

        elif opcode == Opcode.GET_AWAITABLE:
            obj = stack_pop_top(stack)
            stack.push(ASTAwaitable(obj))

        elif opcode in (Opcode.GET_ITER, getattr(Opcode, 'GET_YIELD_FROM_ITER', None)):
            pass

        elif opcode == Opcode.IMPORT_NAME_A:
            if mod.major_ver == 1:
                stack.push(ASTImport(ASTName(code.getName(operand)), None))
            else:
                fromlist = stack_pop_top(stack)
                if mod.ver_compare(2, 5) >= 0:
                    stack.pop() 
                stack.push(ASTImport(ASTName(code.getName(operand)), fromlist))

        elif opcode == Opcode.IMPORT_FROM_A:
            name_node = ASTName(code.getName(operand))
            if stack.top() and getattr(stack.top(), 'type', None) == ASTNodeType.NODE_IMPORT:
                stack.top().add_store(ASTStore(name_node, name_node))
            stack.push(name_node)

        elif opcode == Opcode.IMPORT_STAR:
            import_node = stack_pop_top(stack)
            curblock.append(ASTStore(import_node, None))

        elif opcode == Opcode.IS_OP_A:
            right = stack_pop_top(stack)
            left = stack_pop_top(stack)
            op = 9 if operand else 8
            stack.push(ASTBinary(left, right, op, ASTNodeType.NODE_COMPARE))

        elif opcode in (
            Opcode.JUMP_IF_FALSE_A, Opcode.JUMP_IF_TRUE_A,
            Opcode.JUMP_IF_FALSE_OR_POP_A, Opcode.JUMP_IF_TRUE_OR_POP_A,
            Opcode.POP_JUMP_IF_FALSE_A, Opcode.POP_JUMP_IF_TRUE_A,
            Opcode.POP_JUMP_FORWARD_IF_FALSE_A, Opcode.POP_JUMP_FORWARD_IF_TRUE_A,
            getattr(Opcode, 'INSTRUMENTED_POP_JUMP_IF_FALSE_A', None), getattr(Opcode, 'INSTRUMENTED_POP_JUMP_IF_TRUE_A', None)
        ):
            cond = stack.top()
            ifblk = None
            popped = ASTCondBlock.PopType.UNINITED

            if opcode in (
                Opcode.POP_JUMP_IF_FALSE_A, Opcode.POP_JUMP_IF_TRUE_A,
                Opcode.POP_JUMP_FORWARD_IF_FALSE_A, Opcode.POP_JUMP_FORWARD_IF_TRUE_A,
                getattr(Opcode, 'INSTRUMENTED_POP_JUMP_IF_FALSE_A', None), getattr(Opcode, 'INSTRUMENTED_POP_JUMP_IF_TRUE_A', None)
            ):
                stack.pop()
                popped = ASTCondBlock.PopType.PRE_POPPED

            stack_hist.append(stack.copy())

            if opcode in (Opcode.JUMP_IF_FALSE_OR_POP_A, Opcode.JUMP_IF_TRUE_OR_POP_A):
                stack.pop()
                popped = ASTCondBlock.PopType.POPPED

            neg = opcode in (
                Opcode.JUMP_IF_TRUE_A, Opcode.JUMP_IF_TRUE_OR_POP_A,
                Opcode.POP_JUMP_IF_TRUE_A, Opcode.POP_JUMP_FORWARD_IF_TRUE_A,
                getattr(Opcode, 'INSTRUMENTED_POP_JUMP_IF_TRUE_A', None)
            )

            offs = operand
            if mod.ver_compare(3, 10) >= 0:
                offs *= 2 
            if (mod.ver_compare(3, 12) >= 0 or 
                opcode in (Opcode.JUMP_IF_FALSE_A, Opcode.JUMP_IF_TRUE_A,
                           Opcode.POP_JUMP_FORWARD_IF_TRUE_A, Opcode.POP_JUMP_FORWARD_IF_FALSE_A)):
                offs += pos

            is_exception_match = False
            if getattr(cond, 'type', None) == ASTNodeType.NODE_COMPARE:
                if hasattr(cond, 'op') and cond.op == 10: 
                    is_exception_match = True

            if is_exception_match:
                if (curblock.blktype == ASTBlock.BlkType.BLK_EXCEPT and 
                    isinstance(curblock, ASTCondBlock) and curblock.cond is None):
                    blocks.pop()
                    curblock = blocks[-1] if blocks else None
                    stack_hist.pop()
                ifblk = ASTCondBlock(ASTBlock.BlkType.BLK_EXCEPT, offs, cond.right, False)

            elif curblock.blktype == ASTBlock.BlkType.BLK_ELSE and len(curblock.nodes) == 0:
                blocks.pop()
                stack = stack_hist.pop() 
                stack_hist.pop() 
                ifblk = ASTCondBlock(ASTBlock.BlkType.BLK_ELIF, offs, cond, neg)

            elif (len(curblock.nodes) == 0 and curblock.inited == 0 and 
                  curblock.blktype == ASTBlock.BlkType.BLK_WHILE):
                top = blocks[-1]
                blocks.pop()
                ifblk = ASTCondBlock(top.blktype, offs, cond, neg)
                stack_hist.pop() 

            elif (len(curblock.nodes) == 0 and curblock.end <= offs and 
                  curblock.blktype in (ASTBlock.BlkType.BLK_IF, ASTBlock.BlkType.BLK_ELIF, ASTBlock.BlkType.BLK_WHILE)):
                top = curblock 
                cond1 = top.cond
                blocks.pop()
                if curblock.blktype == ASTBlock.BlkType.BLK_WHILE:
                    stack_hist.pop()
                else:
                    s_top = stack_hist.pop()
                    # stack_hist.pop()
                    stack_hist.append(s_top)
                newcond = None
                if curblock.end == offs or (curblock.end == curpos and not top.negative):
                    newcond = ASTBinary(cond1, cond, ASTBinary.BinOp.BIN_LOG_AND)
                else:
                    newcond = ASTBinary(cond1, cond, ASTBinary.BinOp.BIN_LOG_OR)
                ifblk = ASTCondBlock(top.blktype, offs, newcond, neg)

            elif (curblock.blktype == ASTBlock.BlkType.BLK_FOR and 
                  isinstance(curblock, ASTIterBlock) and curblock.is_comprehension() and 
                  mod.ver_compare(2, 7) >= 0):
                curblock.set_condition(cond)
                stack_hist.pop()
                ifblk = None 
            else:
                ifblk = ASTCondBlock(ASTBlock.BlkType.BLK_IF, offs, cond, neg)

            if ifblk:
                if popped != ASTCondBlock.PopType.UNINITED:
                    ifblk.init(popped)
                blocks.append(ifblk)
                curblock = ifblk

        elif opcode == Opcode.JUMP_ABSOLUTE_A:
            offs = operand
            if mod.ver_compare(3, 10) >= 0:
                offs *= 2

            if offs < pos:
                if curblock.blktype == ASTBlock.BlkType.BLK_FOR:
                    is_jump_to_start = (offs == curblock.start)
                    should_pop = curblock.is_comprehension()
                    should_add = (mod.major_ver == 3 and mod.minor_ver >= 8 and 
                                  is_jump_to_start and not curblock.is_comprehension())
                    if should_pop or should_add:
                        top_node = stack.top()
                        if top_node and getattr(top_node, 'type', None) == ASTNodeType.NODE_COMPREHENSION:
                            comp = top_node
                            if isinstance(comp, ASTComprehension):
                                comp.add_generator(curblock)
                        tmp = curblock
                        blocks.pop()
                        curblock = blocks[-1]
                        if should_add:
                            curblock.append(tmp)

                elif curblock.blktype == ASTBlock.BlkType.BLK_ELSE:
                    stack = stack_hist.pop()
                    blocks.pop()
                    blocks[-1].append(curblock)
                    curblock = blocks[-1]
                    if (curblock.blktype == ASTBlock.BlkType.BLK_CONTAINER and 
                        not getattr(curblock, 'has_finally', False)):
                        blocks.pop()
                        blocks[-1].append(curblock)
                        curblock = blocks[-1]
                else:
                    curblock.append(ASTKeyword(ASTKeyword.Word.KW_CONTINUE))
            
            else:
                if curblock.blktype == ASTBlock.BlkType.BLK_CONTAINER:
                    cont = curblock
                    if getattr(cont, 'has_except', False) and pos < getattr(cont, 'except_off', 0):
                        except_blk = ASTCondBlock(ASTBlock.BlkType.BLK_EXCEPT, 0, None, False)
                        except_blk.init()
                        blocks.append(except_blk)
                        curblock = blocks[-1]
                    continue 

                stack = stack_hist.pop()
                prev = curblock
                nil = None
                push = True
                while True:
                    blocks.pop()
                    if blocks:
                        blocks[-1].append(prev)
                    if prev.blktype in (ASTBlock.BlkType.BLK_IF, ASTBlock.BlkType.BLK_ELIF):
                        if push:
                            stack_hist.append(stack.copy())
                        next_blk = ASTBlock(ASTBlock.BlkType.BLK_ELSE, blocks[-1].end)
                        if prev.inited == ASTCondBlock.PopType.PRE_POPPED:
                            next_blk.init(ASTCondBlock.PopType.PRE_POPPED)
                        blocks.append(next_blk)
                        prev = nil
                    elif prev.blktype == ASTBlock.BlkType.BLK_EXCEPT:
                        if push:
                            stack_hist.append(stack.copy())
                        next_blk = ASTCondBlock(ASTBlock.BlkType.BLK_EXCEPT, blocks[-1].end, None, False)
                        next_blk.init()
                        blocks.append(next_blk)
                        prev = nil
                    elif prev.blktype == ASTBlock.BlkType.BLK_ELSE:
                        prev = blocks[-1]
                        if not push:
                            stack = stack_hist.pop()
                        push = False
                    else:
                        prev = nil
                    if prev == nil:
                        break
                curblock = blocks[-1]

        elif opcode in (Opcode.JUMP_FORWARD_A, getattr(Opcode, 'INSTRUMENTED_JUMP_FORWARD_A', None)):
            offs = operand
            if mod.ver_compare(3, 10) >= 0:
                offs *= 2
            
            if curblock.blktype == ASTBlock.BlkType.BLK_CONTAINER:
                cont = curblock
                if getattr(cont, 'has_except', False):
                    stack_hist.append(stack.copy())
                    curblock.end = pos + offs
                    except_blk = ASTCondBlock(ASTBlock.BlkType.BLK_EXCEPT, pos + offs, None, False)
                    except_blk.init()
                    blocks.append(except_blk)
                    curblock = except_blk
                    continue 

            if stack_hist:
                if stack.empty():
                    stack = stack_hist[-1]
                stack_hist.pop()

            prev = curblock
            nil = None
            push = True

            while True:
                blocks.pop()
                if blocks:
                    blocks[-1].append(prev)
                if prev.blktype in (ASTBlock.BlkType.BLK_IF, ASTBlock.BlkType.BLK_ELIF):
                    if offs == 0:
                        prev = nil
                        break 
                    if push:
                        stack_hist.append(stack.copy())
                    next_blk = ASTBlock(ASTBlock.BlkType.BLK_ELSE, pos + offs)
                    if prev.inited == ASTCondBlock.PopType.PRE_POPPED:
                        next_blk.init(ASTCondBlock.PopType.PRE_POPPED)
                    blocks.append(next_blk)
                    prev = nil
                elif prev.blktype == ASTBlock.BlkType.BLK_EXCEPT:
                    if offs == 0:
                        prev = nil
                        break
                    if push:
                        stack_hist.append(stack.copy())
                    next_blk = ASTCondBlock(ASTBlock.BlkType.BLK_EXCEPT, pos + offs, None, False)
                    next_blk.init()
                    blocks.append(next_blk)
                    prev = nil
                elif prev.blktype == ASTBlock.BlkType.BLK_ELSE:
                    prev = blocks[-1]
                    if not push:
                        stack = stack_hist.pop()
                    push = False
                    if prev.blktype == ASTBlock.BlkType.BLK_MAIN:
                        prev = nil
                elif prev.blktype == ASTBlock.BlkType.BLK_TRY and prev.end < pos + offs:
                    stack = stack_hist.pop()
                    if blocks[-1].blktype == ASTBlock.BlkType.BLK_CONTAINER:
                        cont = blocks[-1]
                        if getattr(cont, 'has_except', False):
                            if push:
                                stack_hist.append(stack.copy())
                            except_blk = ASTCondBlock(ASTBlock.BlkType.BLK_EXCEPT, pos + offs, None, False)
                            except_blk.init()
                            blocks.append(except_blk)
                    else:
                        sys.stderr.write("Something TERRIBLE happened!!\n")
                    prev = nil
                else:
                    prev = nil
                if prev == nil:
                    break

            curblock = blocks[-1]
            if curblock.blktype == ASTBlock.BlkType.BLK_EXCEPT:
                curblock.m_end = pos + offs

        elif opcode in (Opcode.LIST_APPEND, Opcode.LIST_APPEND_A):
            value = stack_pop_top(stack)
            list_node = stack.top()
            if (curblock.blktype == ASTBlock.BlkType.BLK_FOR and 
                isinstance(curblock, ASTIterBlock) and curblock.is_comprehension()):
                stack.pop() 
                stack.push(ASTComprehension(value))
            else:
                stack.push(ASTSubscr(list_node, value)) 

        elif opcode == Opcode.SET_UPDATE_A:
            rhs = stack_pop_top(stack)
            lhs = stack_pop_top(stack) 
            if getattr(rhs, 'type', None) != ASTNodeType.NODE_OBJECT:
                sys.stderr.write("Unsupported argument found for SET_UPDATE\n")
            else:
                obj = rhs.object
                if getattr(obj, 'type', None) != PycObjectType.TYPE_FROZENSET:
                    sys.stderr.write("Unsupported argument type found for SET_UPDATE\n")
                else:
                    if hasattr(obj, 'values'):
                        for it in obj.values:
                            lhs.values.append(ASTObject(it))
                    stack.push(lhs)

        elif opcode == Opcode.LIST_EXTEND_A:
            rhs = stack_pop_top(stack)
            lhs = stack_pop_top(stack) 
            if getattr(rhs, 'type', None) != ASTNodeType.NODE_OBJECT:
                sys.stderr.write("Unsupported argument found for LIST_EXTEND\n")
            else:
                obj = rhs.object
                if getattr(obj, 'type', None) not in (PycObjectType.TYPE_TUPLE, getattr(PycObjectType, 'TYPE_SMALL_TUPLE', 999)):
                    sys.stderr.write("Unsupported argument type found for LIST_EXTEND\n")
                else:
                    if hasattr(obj, 'values'):
                        for it in obj.values:
                            lhs.values.append(ASTObject(it))
                    stack.push(lhs)

        elif opcode == Opcode.LOAD_ATTR_A:
            name = stack.top()
            if getattr(name, 'type', None) != ASTNodeType.NODE_IMPORT:
                stack.pop()
                name_idx = operand
                if mod.ver_compare(3, 12) >= 0:
                    if operand & 1:
                        stack.push(None)
                    name_idx >>= 1
                attr_name = ASTName(code.getName(name_idx))
                stack.push(ASTBinary(name, attr_name, ASTBinary.BinOp.BIN_ATTR))

        elif opcode == Opcode.LOAD_BUILD_CLASS:
            stack.push(ASTLoadBuildClass(PycObject()))

        elif opcode == Opcode.LOAD_CLOSURE_A:
            pass 

        elif opcode == Opcode.LOAD_CONST_A:
            pyc_obj = code.getConst(operand)
            t_ob = ASTObject(pyc_obj)
            if (getattr(pyc_obj, 'type', None) in (PycObjectType.TYPE_TUPLE, getattr(PycObjectType, 'TYPE_SMALL_TUPLE', 999)) and 
                len(getattr(pyc_obj, 'values', [])) == 0):
                stack.push(ASTTuple([]))
            elif getattr(pyc_obj, 'type', None) == PycObjectType.TYPE_NONE:
                stack.push(None)
            else:
                stack.push(t_ob)

        elif opcode in (Opcode.LOAD_DEREF_A, getattr(Opcode, 'LOAD_CLASSDEREF_A', None)):
            stack.push(ASTName(code.getCellVar(mod, operand)))

        elif opcode in (Opcode.LOAD_FAST_A, getattr(Opcode, 'LOAD_FAST_CHECK_A', None), getattr(Opcode, 'LOAD_FAST_CHECK', None), getattr(Opcode, 'LOAD_FAST_AND_CLEAR_A', None)) or getattr(opcode, 'name', '').startswith('LOAD_FAST'):
            if mod.ver_compare(1, 3) < 0:
                stack.push(ASTName(code.getName(operand)))
            else:
                stack.push(ASTName(code.getLocal(operand)))

        elif opcode == getattr(Opcode, 'LOAD_FAST_LOAD_FAST_A', None) or getattr(opcode, 'name', '') == 'LOAD_FAST_LOAD_FAST':
            stack.push(ASTName(code.getLocal(operand >> 4)))
            stack.push(ASTName(code.getLocal(operand & 0xF)))

        elif opcode == Opcode.LOAD_GLOBAL_A:
            name_idx = operand
            if mod.ver_compare(3, 11) >= 0:
                if operand & 1:
                    stack.push(None)
                name_idx >>= 1
            stack.push(ASTName(code.getName(name_idx)))

        elif opcode == Opcode.LOAD_LOCALS:
            stack.push(ASTNode(ASTNodeType.NODE_LOCALS))

        elif opcode == Opcode.STORE_LOCALS:
            stack.pop()

        elif opcode == Opcode.LOAD_METHOD_A:
            name = stack_pop_top(stack)
            method_name = ASTName(code.getName(operand))
            stack.push(ASTBinary(name, method_name, ASTBinary.BinOp.BIN_ATTR))

        elif opcode == Opcode.LOAD_NAME_A:
            stack.push(ASTName(code.getName(operand)))

        elif opcode in (Opcode.MAKE_CLOSURE_A, Opcode.MAKE_FUNCTION_A) or getattr(opcode, 'name', '') in ('MAKE_CLOSURE', 'MAKE_FUNCTION', 'MAKE_CLOSURE_A', 'MAKE_FUNCTION_A'):
            fun_code = stack_pop_top(stack)
            if fun_code is not None and getattr(fun_code, 'type', None) == ASTNodeType.NODE_OBJECT:
                obj_type = fun_code.object.type
                if obj_type not in (PycObjectType.TYPE_CODE, getattr(PycObjectType, 'TYPE_CODE2', 999)):
                    fun_code = stack_pop_top(stack)

            def_args = []
            kw_def_args = []
            if mod.ver_compare(3, 11) >= 0:
                pass 
            else:
                def_count = operand & 0xFF
                kw_def_count = (operand >> 8) & 0xFF
                for _ in range(def_count):
                    def_args.insert(0, stack_pop_top(stack))
                for _ in range(kw_def_count):
                    kw_def_args.insert(0, stack_pop_top(stack))
            stack.push(ASTFunction(fun_code, def_args, kw_def_args))
            
        elif getattr(Opcode, 'SET_FUNCTION_ATTRIBUTE_A', None) == opcode or getattr(opcode, 'name', '') == 'SET_FUNCTION_ATTRIBUTE':
            attr_flag = operand
            attr_val = stack_pop_top(stack)
            func_node = stack.top()
            if func_node and getattr(func_node, 'type', None) == ASTNodeType.NODE_FUNCTION:
                if attr_flag == 1: 
                    if isinstance(attr_val, ASTTuple):
                        func_node.defargs = attr_val.values
                    elif attr_val and getattr(attr_val, 'type', None) == ASTNodeType.NODE_OBJECT and getattr(attr_val.object, 'values', None):
                        func_node.defargs = [ASTObject(v) for v in attr_val.object.values]

        elif opcode == Opcode.NOP:
            pass

        elif opcode == Opcode.POP_BLOCK:
            if curblock.blktype in (ASTBlock.BlkType.BLK_CONTAINER, ASTBlock.BlkType.BLK_FINALLY):
                pass
            elif curblock.blktype == ASTBlock.BlkType.BLK_WITH:
                pass
            else:
                if curblock.nodes and getattr(curblock.nodes[-1], 'type', None) == ASTNodeType.NODE_KEYWORD:
                    curblock.remove_last()
                
                if curblock.blktype in (ASTBlock.BlkType.BLK_IF, ASTBlock.BlkType.BLK_ELIF, 
                                      ASTBlock.BlkType.BLK_ELSE, ASTBlock.BlkType.BLK_TRY,
                                      ASTBlock.BlkType.BLK_EXCEPT, ASTBlock.BlkType.BLK_FINALLY):
                    if stack_hist:
                        stack = stack_hist[-1]
                        stack_hist.pop()
                    else:
                        sys.stderr.write("Warning: Stack history is empty\n")
                
                tmp = curblock
                blocks.pop()
                if blocks:
                    curblock = blocks[-1]
                
                if not (tmp.blktype == ASTBlock.BlkType.BLK_ELSE and not tmp.nodes):
                    curblock.append(tmp)
                
                if tmp.blktype == ASTBlock.BlkType.BLK_FOR and tmp.end >= pos:
                    stack_hist.append(stack.copy())
                    blkelse = ASTBlock(ASTBlock.BlkType.BLK_ELSE, tmp.end)
                    blocks.append(blkelse)
                    curblock = blkelse
                
                if (curblock.blktype == ASTBlock.BlkType.BLK_TRY and 
                    tmp.blktype not in (ASTBlock.BlkType.BLK_FOR, ASTBlock.BlkType.BLK_ASYNCFOR, ASTBlock.BlkType.BLK_WHILE)):
                    if stack_hist:
                        stack = stack_hist[-1]
                        stack_hist.pop()
                    tmp = curblock
                    blocks.pop()
                    curblock = blocks[-1]
                    if not (tmp.blktype == ASTBlock.BlkType.BLK_ELSE and not tmp.nodes):
                        curblock.append(tmp)
                
                if curblock.blktype == ASTBlock.BlkType.BLK_CONTAINER:
                    cont = curblock
                    has_finally = getattr(cont, 'has_finally', False)
                    has_except = getattr(cont, 'has_except', False)
                    if tmp.blktype == ASTBlock.BlkType.BLK_ELSE and not has_finally:
                        blocks.pop()
                        curblock = blocks[-1]
                        curblock.append(cont)
                    elif ((tmp.blktype == ASTBlock.BlkType.BLK_ELSE and has_finally) or 
                          (tmp.blktype == ASTBlock.BlkType.BLK_TRY and not has_except)):
                        stack_hist.append(stack.copy())
                        final_blk = ASTBlock(ASTBlock.BlkType.BLK_FINALLY, 0, 1) 
                        blocks.append(final_blk)
                        curblock = final_blk
                
                if (curblock.blktype in (ASTBlock.BlkType.BLK_FOR, ASTBlock.BlkType.BLK_ASYNCFOR) and 
                    curblock.end == pos):
                    blocks.pop()
                    blocks[-1].append(curblock)
                    curblock = blocks[-1]

        elif opcode == Opcode.POP_EXCEPT:
            pass

        elif opcode == Opcode.POP_TOP:
            value = stack_pop_top(stack)
            if curblock.inited == 0:
                if curblock.blktype == ASTBlock.BlkType.BLK_WITH:
                    curblock.set_expr(value)
                else:
                    curblock.init()
            elif value is None or getattr(value, 'processed', False):
                pass
            else:
                if getattr(value, 'type', None) == ASTNodeType.NODE_OBJECT:
                    if getattr(value.object, 'type', None) == getattr(PycObjectType, 'TYPE_NONE', None):
                        continue
                curblock.append(value)
                if (curblock.blktype == ASTBlock.BlkType.BLK_FOR and 
                    isinstance(curblock, ASTIterBlock) and curblock.is_comprehension()):
                    if getattr(value, 'type', None) == ASTNodeType.NODE_CALL:
                        pparams = value.pparams
                        if pparams:
                            res = pparams[0]
                            stack.push(ASTComprehension(res))

        elif opcode == Opcode.PRINT_ITEM:
            print_node = None
            if curblock.nodes and getattr(curblock.nodes[-1], 'type', None) == ASTNodeType.NODE_PRINT:
                print_node = curblock.nodes[-1]
            if (print_node and print_node.stream is None and not print_node.eol):
                print_node.add(stack.top())
            else:
                curblock.append(ASTPrint(stack.top()))
            stack.pop()

        elif opcode == Opcode.PRINT_ITEM_TO:
            stream = stack_pop_top(stack)
            print_node = None
            if curblock.nodes and getattr(curblock.nodes[-1], 'type', None) == ASTNodeType.NODE_PRINT:
                print_node = curblock.nodes[-1]
            if (print_node and print_node.stream == stream and not print_node.eol):
                print_node.add(stack.top())
            else:
                curblock.append(ASTPrint(stack.top(), stream))
            stack.pop()
            stream.processed = True

        elif opcode == Opcode.PRINT_NEWLINE:
            print_node = None
            if curblock.nodes and getattr(curblock.nodes[-1], 'type', None) == ASTNodeType.NODE_PRINT:
                print_node = curblock.nodes[-1]
            if (print_node and print_node.stream is None and not print_node.eol):
                print_node.eol = True
            else:
                curblock.append(ASTPrint(None))
            stack.pop()

        elif opcode == Opcode.PRINT_NEWLINE_TO:
            stream = stack_pop_top(stack)
            print_node = None
            if curblock.nodes and getattr(curblock.nodes[-1], 'type', None) == ASTNodeType.NODE_PRINT:
                print_node = curblock.nodes[-1]
            if (print_node and print_node.stream == stream and not print_node.eol):
                print_node.eol = True
            else:
                curblock.append(ASTPrint(None, stream))
            stack.pop()
            stream.processed = True

        elif opcode == Opcode.RAISE_VARARGS_A:
            params = []
            for _ in range(operand):
                params.insert(0, stack_pop_top(stack))
            curblock.append(ASTRaise(params))
            if ((curblock.blktype == ASTBlock.BlkType.BLK_IF or curblock.blktype == ASTBlock.BlkType.BLK_ELSE) and 
                stack_hist and mod.ver_compare(2, 6) >= 0):
                stack = stack_hist[-1]
                stack_hist.pop()
                prev = curblock
                blocks.pop()
                curblock = blocks[-1]
                curblock.append(prev)

        elif opcode in (Opcode.RETURN_VALUE, getattr(Opcode, 'INSTRUMENTED_RETURN_VALUE_A', None)):
            val = stack_pop_top(stack)
            curblock.append(ASTReturn(val))
            if ((curblock.blktype == ASTBlock.BlkType.BLK_IF or curblock.blktype == ASTBlock.BlkType.BLK_ELSE) and 
                stack_hist and mod.ver_compare(2, 6) >= 0):
                stack = stack_hist[-1]
                stack_hist.pop()
                prev = curblock
                blocks.pop()
                curblock = blocks[-1]
                curblock.append(prev)

        elif opcode in (getattr(Opcode, 'RETURN_CONST_A', None), getattr(Opcode, 'INSTRUMENTED_RETURN_CONST_A', None)):
            val = ASTObject(code.getConst(operand))
            curblock.append(ASTReturn(val))

        elif opcode == Opcode.ROT_TWO:
            one = stack_pop_top(stack)
            if getattr(stack.top(), 'type', None) == ASTNodeType.NODE_CHAINSTORE:
                stack.pop()
            two = stack_pop_top(stack)
            stack.push(one)
            stack.push(two)

        elif opcode == Opcode.ROT_THREE:
            one = stack_pop_top(stack)
            two = stack_pop_top(stack)
            if getattr(stack.top(), 'type', None) == ASTNodeType.NODE_CHAINSTORE:
                stack.pop()
            three = stack_pop_top(stack)
            stack.push(one)
            stack.push(three)
            stack.push(two)

        elif opcode == Opcode.ROT_FOUR:
            one = stack_pop_top(stack)
            two = stack_pop_top(stack)
            three = stack_pop_top(stack)
            if getattr(stack.top(), 'type', None) == ASTNodeType.NODE_CHAINSTORE:
                stack.pop()
            four = stack_pop_top(stack)
            stack.push(one)
            stack.push(four)
            stack.push(three)
            stack.push(two)

        elif opcode == Opcode.SET_LINENO_A:
            pass

        elif opcode in (Opcode.SETUP_WITH_A, Opcode.WITH_EXCEPT_START):
            withblock = ASTWithBlock(pos + operand)
            blocks.append(withblock)
            curblock = withblock

        elif opcode in (Opcode.WITH_CLEANUP, Opcode.WITH_CLEANUP_START):
            none_node = stack_pop_top(stack)
            if none_node is not None:
                sys.stderr.write("Something TERRIBLE happened!\n")
            else:
                if curblock.blktype == ASTBlock.BlkType.BLK_WITH and curblock.end == curpos:
                    with_blk = curblock
                    blocks.pop()
                    curblock = blocks[-1]
                    curblock.append(with_blk)
                else:
                    sys.stderr.write(f"Something TERRIBLE happened! No matching with block found for WITH_CLEANUP at {curpos}\n")

        elif opcode == Opcode.WITH_CLEANUP_FINISH:
            pass
            
        elif opcode == Opcode.SETUP_EXCEPT_A:
            if curblock.blktype == ASTBlock.BlkType.BLK_CONTAINER:
                if hasattr(curblock, 'set_except'):
                    curblock.set_except(pos + operand)
                else:
                    curblock.except_off = pos + operand 
            else:
                if 'ASTContainerBlock' in globals():
                    next_blk = ASTContainerBlock(0, pos + operand)
                else:
                    next_blk = ASTBlock(ASTBlock.BlkType.BLK_CONTAINER, 0)
                    next_blk.except_off = pos + operand
                blocks.append(next_blk)
            stack_hist.append(stack.copy())
            tryblock = ASTBlock(ASTBlock.BlkType.BLK_TRY, pos + operand)
            tryblock.handled = True 
            blocks.append(tryblock)
            curblock = tryblock
            need_try = False

        elif opcode == Opcode.SETUP_FINALLY_A:
            if 'ASTContainerBlock' in globals():
                next_blk = ASTContainerBlock(pos + operand)
            else:
                next_blk = ASTBlock(ASTBlock.BlkType.BLK_CONTAINER, 0)
                next_blk.finally_off = pos + operand
            blocks.append(next_blk)
            curblock = next_blk
            need_try = True

        elif opcode == Opcode.SETUP_LOOP_A:
            next_blk = ASTCondBlock(ASTBlock.BlkType.BLK_WHILE, pos + operand, None, False)
            blocks.append(next_blk)
            curblock = next_blk

        elif opcode == Opcode.SLICE_0:
            name = stack_pop_top(stack)
            slice_node = ASTSlice(ASTSlice.SliceOp.SLICE0)
            stack.push(ASTSubscr(name, slice_node))

        elif opcode == Opcode.SLICE_1:
            lower = stack_pop_top(stack)
            name = stack_pop_top(stack)
            slice_node = ASTSlice(ASTSlice.SliceOp.SLICE1, lower)
            stack.push(ASTSubscr(name, slice_node))

        elif opcode == Opcode.SLICE_2:
            upper = stack_pop_top(stack)
            name = stack_pop_top(stack)
            slice_node = ASTSlice(ASTSlice.SliceOp.SLICE2, None, upper)
            stack.push(ASTSubscr(name, slice_node))

        elif opcode == Opcode.SLICE_3:
            upper = stack_pop_top(stack)
            lower = stack_pop_top(stack)
            name = stack_pop_top(stack)
            slice_node = ASTSlice(ASTSlice.SliceOp.SLICE3, lower, upper)
            stack.push(ASTSubscr(name, slice_node))

        elif opcode == Opcode.STORE_ATTR_A:
            if unpack > 0:
                owner = stack_pop_top(stack)
                attr = ASTBinary(owner, ASTName(code.getName(operand)), ASTBinary.BinOp.BIN_ATTR)
                tup = stack.top()
                if hasattr(tup, 'add'): tup.add(attr)
                unpack -= 1
                if unpack <= 0:
                    stack.pop()
                    seq = stack_pop_top(stack)
                    if seq is not None and getattr(seq, 'type', None) == ASTNodeType.NODE_CHAINSTORE:
                        append_to_chain_store(seq, tup, stack, curblock)
                    else:
                        curblock.append(ASTStore(seq, tup))
            else:
                owner = stack_pop_top(stack)
                value = stack_pop_top(stack)
                attr = ASTBinary(owner, ASTName(code.getName(operand)), ASTBinary.BinOp.BIN_ATTR)
                if value is not None and getattr(value, 'type', None) == ASTNodeType.NODE_CHAINSTORE:
                    append_to_chain_store(value, attr, stack, curblock)
                else:
                    curblock.append(ASTStore(value, attr))

        elif opcode == Opcode.STORE_DEREF_A:
            if unpack > 0:
                name = ASTName(code.getCellVar(mod, operand))
                tup = stack.top()
                if getattr(tup, 'type', None) == ASTNodeType.NODE_TUPLE: tup.add(name)
                unpack -= 1
                if unpack <= 0:
                    stack.pop()
                    seq = stack_pop_top(stack)
                    if getattr(seq, 'type', None) == ASTNodeType.NODE_CHAINSTORE:
                        append_to_chain_store(seq, tup, stack, curblock)
                    else:
                        curblock.append(ASTStore(seq, tup))
            else:
                value = stack_pop_top(stack)
                name = ASTName(code.getCellVar(mod, operand))
                if value is not None and getattr(value, 'type', None) == ASTNodeType.NODE_IMPORT:
                    value.add_store(ASTStore(value, name))
                    if value != stack.top():
                        curblock.append(value)
                elif value is not None and getattr(value, 'type', None) == ASTNodeType.NODE_CHAINSTORE:
                    append_to_chain_store(value, name, stack, curblock)
                else:
                    curblock.append(ASTStore(value, name))

        elif opcode in (Opcode.STORE_NAME_A, Opcode.STORE_GLOBAL_A, getattr(Opcode, 'STORE_FAST_A', None)) or getattr(opcode, 'name', '') in ('STORE_NAME', 'STORE_GLOBAL', 'STORE_FAST', 'STORE_FAST_A', 'STORE_NAME_A', 'STORE_GLOBAL_A'):
            if getattr(opcode, 'name', '').startswith('STORE_FAST') or opcode == getattr(Opcode, 'STORE_FAST_A', None):
                if mod.ver_compare(1, 3) < 0:
                    name_obj = code.getName(operand)
                else:
                    name_obj = code.getLocal(operand)
            else:
                name_obj = code.getName(operand)
                
            if len(name_obj.value) >= 2 and name_obj.value.startswith(b"_["):
                pass
            elif getattr(opcode, 'name', '').startswith('STORE_NAME') or getattr(opcode, 'name', '').startswith('STORE_GLOBAL') or opcode in (Opcode.STORE_NAME_A, Opcode.STORE_GLOBAL_A):
                class_prefix = b"_" + code.name.value
                if name_obj.value.startswith(class_prefix + b"__"):
                    name_obj.value = name_obj.value[len(class_prefix):]
                    
            name_node = ASTName(name_obj)
            
            if unpack > 0:
                tup = stack.top()
                if getattr(tup, 'type', None) == ASTNodeType.NODE_TUPLE: tup.add(name_node)
                unpack -= 1
                if unpack <= 0:
                    stack.pop()
                    seq = stack_pop_top(stack)
                    if curblock.blktype == ASTBlock.BlkType.BLK_FOR and curblock.inited == 0:
                        if isinstance(tup, ASTTuple): tup.set_require_parens(False)
                        curblock.set_index(tup)
                    elif getattr(seq, 'type', None) == ASTNodeType.NODE_CHAINSTORE:
                        append_to_chain_store(seq, tup, stack, curblock)
                    else:
                        curblock.append(ASTStore(seq, tup))
            else:
                value = stack_pop_top(stack)
                
                # --- Unifying and absorbing IMPORT correctly to avoid blank lines and dummy stores ---
                if stack.top() and getattr(stack.top(), 'type', None) == ASTNodeType.NODE_IMPORT:
                    import_node = stack.top()
                    if hasattr(import_node, 'stores') and import_node.stores and is_equal_name(import_node.stores[-1].src, value):
                        import_node.stores[-1] = ASTStore(import_node.stores[-1].src, name_node)
                        if opcode == Opcode.STORE_GLOBAL_A or getattr(opcode, 'name', '') == 'STORE_GLOBAL':
                            code.markGlobal(name_node.name)
                        continue 

                if curblock.blktype == ASTBlock.BlkType.BLK_FOR and curblock.inited == 0:
                    curblock.set_index(name_node)
                elif value is not None and getattr(value, 'type', None) == ASTNodeType.NODE_IMPORT:
                    value.add_store(ASTStore(value, name_node))
                    if value != stack.top():
                        curblock.append(value)
                elif curblock.blktype == ASTBlock.BlkType.BLK_WITH and curblock.inited == 0:
                    curblock.set_expr(value)
                    curblock.set_var(name_node)
                elif value is not None and getattr(value, 'type', None) == ASTNodeType.NODE_CHAINSTORE:
                    append_to_chain_store(value, name_node, stack, curblock)
                else:
                    if value is None or getattr(value, 'type', None) != getattr(ASTNodeType, 'NODE_INVALID', -1):
                        curblock.append(ASTStore(value, name_node))

            if opcode == Opcode.STORE_GLOBAL_A or getattr(opcode, 'name', '') == 'STORE_GLOBAL':
                code.markGlobal(name_node.name)

        elif opcode == Opcode.STORE_SLICE_0:
            dest = stack_pop_top(stack)
            value = stack_pop_top(stack)
            target = ASTSubscr(dest, ASTSlice(ASTSlice.SliceOp.SLICE0))
            curblock.append(ASTStore(value, target))

        elif opcode == Opcode.STORE_SLICE_1:
            upper = stack_pop_top(stack)
            dest = stack_pop_top(stack)
            value = stack_pop_top(stack)
            target = ASTSubscr(dest, ASTSlice(ASTSlice.SliceOp.SLICE1, upper))
            curblock.append(ASTStore(value, target))

        elif opcode == Opcode.STORE_SLICE_2:
            lower = stack_pop_top(stack)
            dest = stack_pop_top(stack)
            value = stack_pop_top(stack)
            target = ASTSubscr(dest, ASTSlice(ASTSlice.SliceOp.SLICE2, lower, None))
            curblock.append(ASTStore(value, target))

        elif opcode == Opcode.STORE_SLICE_3:
            lower = stack_pop_top(stack)
            upper = stack_pop_top(stack)
            dest = stack_pop_top(stack)
            value = stack_pop_top(stack)
            target = ASTSubscr(dest, ASTSlice(ASTSlice.SliceOp.SLICE3, lower, upper))
            curblock.append(ASTStore(value, target))
        
        elif opcode == Opcode.STORE_SUBSCR:
            if unpack > 0:
                key = stack_pop_top(stack)
                container = stack_pop_top(stack)
                save = ASTSubscr(container, key)
                tup = stack.top()
                if hasattr(tup, 'add'): tup.add(save)
                unpack -= 1
                if unpack <= 0:
                    stack.pop() 
                    seq = stack_pop_top(stack)
                    if seq is not None and getattr(seq, 'type', None) == ASTNodeType.NODE_CHAINSTORE:
                        append_to_chain_store(seq, tup, stack, curblock)
                    else:
                        curblock.append(ASTStore(seq, tup))
            else:
                key = stack_pop_top(stack)
                container = stack_pop_top(stack)
                value = stack_pop_top(stack)
                found_annotated_var = (
                    variable_annotations and container is not None and 
                    getattr(container, 'type', None) == ASTNodeType.NODE_NAME and 
                    container.name.value == b"__annotations__"
                )
                if found_annotated_var:
                    if curblock.nodes and getattr(curblock.nodes[-1], 'type', None) == ASTNodeType.NODE_STORE:
                        store_node = curblock.nodes[-1]
                        curblock.remove_last()
                        curblock.append(ASTStore(store_node.src, ASTAnnotatedVar(key, value)))
                    else:
                        curblock.append(ASTAnnotatedVar(key, value))
                else:
                    if container is not None and getattr(container, 'type', None) == ASTNodeType.NODE_MAP:
                        container.add(key, value)
                    elif value is not None and getattr(value, 'type', None) == ASTNodeType.NODE_CHAINSTORE:
                        append_to_chain_store(value, ASTSubscr(container, key), stack, curblock)
                    else:
                        curblock.append(ASTStore(value, ASTSubscr(container, key)))

        elif opcode == Opcode.UNARY_CALL:
            func = stack_pop_top(stack)
            stack.push(ASTCall(func, [], []))

        elif opcode == Opcode.UNARY_CONVERT:
            name = stack_pop_top(stack)
            stack.push(ASTConvert(name))

        elif opcode == Opcode.UNARY_INVERT:
            arg = stack_pop_top(stack)
            stack.push(ASTUnary(arg, ASTUnary.UnOp.UN_INVERT))

        elif opcode == Opcode.UNARY_NEGATIVE:
            arg = stack_pop_top(stack)
            stack.push(ASTUnary(arg, ASTUnary.UnOp.UN_NEGATIVE))

        elif opcode == Opcode.UNARY_NOT:
            arg = stack_pop_top(stack)
            stack.push(ASTUnary(arg, ASTUnary.UnOp.UN_NOT))

        elif opcode == Opcode.UNARY_POSITIVE:
            arg = stack_pop_top(stack)
            stack.push(ASTUnary(arg, ASTUnary.UnOp.UN_POSITIVE))

        elif opcode in (Opcode.UNPACK_LIST_A, Opcode.UNPACK_TUPLE_A, Opcode.UNPACK_SEQUENCE_A):
            unpack = operand
            if unpack > 0:
                stack.push(ASTTuple([]))
            else:
                tup = ASTTuple([])
                if curblock.blktype == ASTBlock.BlkType.BLK_FOR and curblock.inited == 0:
                    tup.set_require_parens(True)
                    curblock.set_index(tup)
                elif getattr(stack.top(), 'type', None) == ASTNodeType.NODE_CHAINSTORE:
                    chain_store = stack_pop_top(stack)
                    append_to_chain_store(chain_store, tup, stack, curblock)
                else:
                    target = stack_pop_top(stack)
                    curblock.append(ASTStore(target, tup))

        elif opcode == Opcode.YIELD_FROM:
            dest = stack_pop_top(stack)
            value = stack.top()
            if value:
                value.processed = True
                curblock.append(ASTReturn(value, ASTReturn.RetType.YIELD_FROM))

        elif opcode in (Opcode.YIELD_VALUE, getattr(Opcode, 'INSTRUMENTED_YIELD_VALUE_A', None)):
            value = stack_pop_top(stack)
            curblock.append(ASTReturn(value, ASTReturn.RetType.YIELD))

        elif opcode == Opcode.SETUP_ANNOTATIONS:
            variable_annotations = True 

        elif opcode in (Opcode.PRECALL_A, Opcode.RESUME_A, getattr(Opcode, 'INSTRUMENTED_RESUME_A', None), getattr(Opcode, 'CACHE', None)):
            pass

        elif getattr(Opcode, 'PUSH_NULL', None) == opcode or getattr(opcode, 'name', '') == 'PUSH_NULL':
            stack.push(None)

        elif opcode == Opcode.GEN_START_A:
            stack.pop()

        elif opcode in (getattr(Opcode, 'SWAP', None), getattr(Opcode, 'SWAP_A', None)) or getattr(opcode, 'name', '') in ('SWAP', 'SWAP_A'):
            idx = operand
            if idx > 1:
                items = []
                for _ in range(idx):
                    items.append(stack_pop_top(stack))
                items[0], items[-1] = items[-1], items[0]
                for item in reversed(items):
                    stack.push(item)
                    
        elif opcode in (getattr(Opcode, 'COPY', None), getattr(Opcode, 'COPY_A', None)) or getattr(opcode, 'name', '') in ('COPY', 'COPY_A'):
            idx = operand
            items = []
            for _ in range(idx):
                items.append(stack_pop_top(stack))
            target = items[-1] 
            for item in reversed(items):
                stack.push(item)
            stack.push(target)

        elif getattr(Opcode, 'PUSH_EXC_INFO_A', None) == opcode or getattr(opcode, 'name', '') in ('PUSH_EXC_INFO', 'PUSH_EXC_INFO_A'):
            val = stack_pop_top(stack)
            # Push a dummy node representing the current exception to keep the stack balanced
            stack.push(ASTName(PycString(b"exc_info")))
            stack.push(val)

        elif getattr(Opcode, 'JUMP_BACKWARD_A', None) == opcode or getattr(opcode, 'name', '') in ('JUMP_BACKWARD', 'JUMP_BACKWARD_A'):
            # JUMP_BACKWARD offset is relative and multiplied by 2 in 3.11+
            offs = pos - (operand * 2)
            
            # The logic exactly mirrors the JUMP_ABSOLUTE_A backward jump handler
            if curblock.blktype == ASTBlock.BlkType.BLK_FOR:
                is_jump_to_start = (offs == curblock.start)
                should_pop = curblock.is_comprehension()
                should_add = (mod.major_ver == 3 and mod.minor_ver >= 8 and 
                              is_jump_to_start and not curblock.is_comprehension())

                if should_pop or should_add:
                    top_node = stack.top()
                    if top_node and getattr(top_node, 'type', None) == ASTNodeType.NODE_COMPREHENSION:
                        comp = top_node
                        if isinstance(comp, ASTComprehension):
                            comp.add_generator(curblock)
                    
                    tmp = curblock
                    blocks.pop()
                    curblock = blocks[-1]
                    if should_add:
                        curblock.append(tmp)

            elif curblock.blktype == ASTBlock.BlkType.BLK_ELSE:
                stack = stack_hist.pop()
                blocks.pop()
                blocks[-1].append(curblock)
                curblock = blocks[-1]

                if (curblock.blktype == ASTBlock.BlkType.BLK_CONTAINER and 
                    not getattr(curblock, 'has_finally', False)):
                    blocks.pop()
                    blocks[-1].append(curblock)
                    curblock = blocks[-1]
            else:
                curblock.append(ASTKeyword(ASTKeyword.Word.KW_CONTINUE))

        elif getattr(Opcode, 'RERAISE_A', None) == opcode or getattr(opcode, 'name', '') in ('RERAISE', 'RERAISE_A'):
            if operand != 0:
                stack.pop() # Pops f_lasti if oparg is non-zero
            exc = stack_pop_top(stack)
            # RERAISE translates to a bare 'raise' statement inside exception handlers
            curblock.append(ASTRaise([]))

        elif getattr(Opcode, 'COPY_FREE_VARS_A', None) == opcode or getattr(opcode, 'name', '') in ('COPY_FREE_VARS', 'COPY_FREE_VARS_A'):
            # Internal CPython VM setup for closures. No AST effect needed.
            pass

        elif getattr(Opcode, 'MAKE_CELL_A', None) == opcode or getattr(opcode, 'name', '') in ('MAKE_CELL', 'MAKE_CELL_A'):
            # Internal CPython VM setup for cell variables. No AST effect needed.
            pass

        elif getattr(Opcode, 'CHECK_EXC_MATCH', None) == opcode or getattr(opcode, 'name', '') == 'CHECK_EXC_MATCH':
            match_type = stack_pop_top(stack) # The exception type to match against (STACK[-1])
            exc_value = stack.top()           # The actual exception (STACK[-2] remains on stack)
            
            # Compare operator 10 is EXCEPTION_MATCH (except:) in the PyCDC AST mapping
            cmp_node = ASTBinary(exc_value, match_type, 10, getattr(ASTNodeType, 'NODE_COMPARE', 999))
            stack.push(cmp_node)
        elif getattr(Opcode, 'LOAD_SUPER_ATTR_A', None) == opcode or getattr(opcode, 'name', '') in ('LOAD_SUPER_ATTR', 'LOAD_SUPER_ATTR_A'):
            # The operand packs three pieces of information
            name_idx = operand >> 2
            is_method_load = operand & 1
            is_two_arg = operand & 2
            
            # Pop the three values off the stack
            self_arg = stack_pop_top(stack)
            cls_arg = stack_pop_top(stack)
            super_global = stack_pop_top(stack)
            
            # Construct the super() or super(cls, self) call
            pos_args = []
            if is_two_arg:
                pos_args = [cls_arg, self_arg]
                
            super_call = ASTCall(super_global, pos_args, [])
            
            # Get the attribute name and bind it to the super() call
            attr_name = ASTName(code.getName(name_idx))
            attr_access = ASTBinary(super_call, attr_name, ASTBinary.BinOp.BIN_ATTR)
            
            # If it's a method load, push a NULL onto the stack first
            if is_method_load:
                stack.push(None)
                
            stack.push(attr_access)
        elif getattr(Opcode, 'MAP_ADD_A', None) == opcode or getattr(opcode, 'name', '') in ('MAP_ADD', 'MAP_ADD_A'):
            # Python 3.8+ changed the order of key and value on the stack
            if mod.ver_compare(3, 8) >= 0:
                value = stack_pop_top(stack)
                key = stack_pop_top(stack)
            else:
                key = stack_pop_top(stack)
                value = stack_pop_top(stack)
            
            # The dictionary is sitting right below the popped items
            map_node = stack.top()
            
            if curblock.blktype == ASTBlock.BlkType.BLK_FOR and getattr(curblock, 'is_comprehension', lambda: False)():
                if map_node and getattr(map_node, 'type', None) == ASTNodeType.NODE_MAP:
                    map_node.add(key, value)
                else:
                    stack.pop() 
                    temp_map = ASTMap()
                    temp_map.add(key, value)
                    stack.push(ASTComprehension(temp_map))
            else:
                if map_node and getattr(map_node, 'type', None) == ASTNodeType.NODE_MAP:
                    map_node.add(key, value)

        elif getattr(Opcode, 'END_FOR_A', None) == opcode or getattr(opcode, 'name', '') in ('END_FOR', 'END_FOR_A'):
            # In Python 3.12, END_FOR is essentially POP_TOP used specifically for loops
            stack_pop_top(stack)

        elif getattr(Opcode, 'BEFORE_WITH_A', None) == opcode or getattr(opcode, 'name', '') in ('BEFORE_WITH', 'BEFORE_WITH_A'):
            # Create the with block scope
            end_pos = pos + operand if operand else 0
            withblock = ASTWithBlock(end_pos)
            blocks.append(withblock)
            curblock = withblock
            
            # In Python 3.11+, BEFORE_WITH executes the context manager, 
            # pushing __exit__ and the __enter__() result onto the stack.
            # We simulate this stack growth so STORE_FAST processes it correctly.
            ctx_mgr = stack_pop_top(stack)
            stack.push(ASTName(PycString( b"__exit__")))
            stack.push(ctx_mgr)
        else:
            sys.stderr.write(f"Unsupported opcode: {getattr(opcode, 'name', str(opcode))} ({getattr(opcode, 'value', str(opcode))})\n")
            clean_build = False

        else_pop = (
            (curblock.blktype == ASTBlock.BlkType.BLK_ELSE) or
            (curblock.blktype == ASTBlock.BlkType.BLK_IF) or
            (curblock.blktype == ASTBlock.BlkType.BLK_ELIF)
        ) and (curblock.end == pos)

    if stack_hist:
        sys.stderr.write("Warning: Stack history is not empty!\n")
    
    if len(blocks) > 1:
        sys.stderr.write("Warning: block stack is not empty!\n")
        while len(blocks) > 1:
            tmp = blocks.pop()
            blocks[-1].append(tmp)

    clean_build = True
    return ASTNodeList(defblock.nodes)


def cmp_prec(parent: ASTNode, child: ASTNode) -> int:
    if getattr(parent, 'type', None) == ASTNodeType.NODE_UNARY:
        if isinstance(parent, ASTUnary) and parent.op == ASTUnary.UnOp.UN_NOT:
            return 1
    if getattr(child, 'type', None) == ASTNodeType.NODE_BINARY:
        bin_child = child 
        if getattr(parent, 'type', None) == ASTNodeType.NODE_BINARY:
            bin_parent = parent
            if bin_parent.right == child:
                if (bin_parent.op == ASTBinary.BinOp.BIN_SUBTRACT and bin_child.op == ASTBinary.BinOp.BIN_ADD):
                    return 1
                elif (bin_parent.op == ASTBinary.BinOp.BIN_DIVIDE and bin_child.op == ASTBinary.BinOp.BIN_MULTIPLY):
                    return 1
            return bin_child.op - bin_parent.op
        elif getattr(parent, 'type', None) == getattr(ASTNodeType, 'NODE_COMPARE', 999):
             return 1 if (bin_child.op == ASTBinary.BinOp.BIN_LOG_AND or bin_child.op == ASTBinary.BinOp.BIN_LOG_OR) else -1
        elif getattr(parent, 'type', None) == ASTNodeType.NODE_UNARY:
            return -1 if bin_child.op == ASTBinary.BinOp.BIN_POWER else 1
            
    elif getattr(child, 'type', None) == ASTNodeType.NODE_UNARY:
        un_child = child
        if getattr(parent, 'type', None) == ASTNodeType.NODE_BINARY:
            bin_parent = parent
            if bin_parent.op in (ASTBinary.BinOp.BIN_LOG_AND, ASTBinary.BinOp.BIN_LOG_OR): return -1
            elif un_child.op == ASTUnary.UnOp.UN_NOT: return 1
            elif bin_parent.op == ASTBinary.BinOp.BIN_POWER: return 1
            else: return -1
        elif getattr(parent, 'type', None) == getattr(ASTNodeType, 'NODE_COMPARE', 999):
            return 1 if un_child.op == ASTUnary.UnOp.UN_NOT else -1
        elif getattr(parent, 'type', None) == ASTNodeType.NODE_UNARY:
            return un_child.op - parent.op
            
    elif getattr(child, 'type', None) == getattr(ASTNodeType, 'NODE_COMPARE', 999):
        cmp_child = child
        if getattr(parent, 'type', None) == ASTNodeType.NODE_BINARY:
            bin_parent = parent
            return -1 if (bin_parent.op == ASTBinary.BinOp.BIN_LOG_AND or bin_parent.op == ASTBinary.BinOp.BIN_LOG_OR) else 1
        elif getattr(parent, 'type', None) == getattr(ASTNodeType, 'NODE_COMPARE', 999):
            return cmp_child.op - parent.op
        elif getattr(parent, 'type', None) == ASTNodeType.NODE_UNARY:
             return -1 if parent.op == ASTUnary.UnOp.UN_NOT else 1
    return -1

def print_ordered(parent: ASTNode, child: ASTNode, mod: PycModule, pyc_output: TextIO):
    t = getattr(child, 'type', None)
    if t in (ASTNodeType.NODE_BINARY, getattr(ASTNodeType, 'NODE_COMPARE', 999), ASTNodeType.NODE_UNARY):
        if cmp_prec(parent, child) > 0:
            pyc_output.write("(")
            print_src(child, mod, pyc_output)
            pyc_output.write(")")
        else:
            print_src(child, mod, pyc_output)
    else:
        print_src(child, mod, pyc_output)

def start_line(indent: int, pyc_output: TextIO):
    if in_lambda: return
    pyc_output.write("    " * indent)

def end_line(pyc_output: TextIO):
    if in_lambda: return
    pyc_output.write("\n")

def print_block(blk: ASTBlock, mod: PycModule, pyc_output: TextIO):
    lines = []
    for ln in blk.nodes:
        if getattr(ln, 'type', None) == ASTNodeType.NODE_STORE:
            if ln.src is not None and ln.dest is not None and is_equal_name(ln.src, ln.dest):
                continue
        lines.append(ln)

    if not lines:
        pass_node = ASTKeyword(ASTKeyword.Word.KW_PASS)
        start_line(cur_indent, pyc_output)
        print_src(pass_node, mod, pyc_output)
        return
    
    for i, ln in enumerate(lines):
        if getattr(ln, 'type', None) != ASTNodeType.NODE_NODELIST:
            start_line(cur_indent, pyc_output)
        print_src(ln, mod, pyc_output)
        if i + 1 != len(lines):
            end_line(pyc_output)

def print_formatted_value(node: ASTFormattedValue, mod: PycModule, pyc_output: TextIO):
    pyc_output.write("{")
    print_src(node.val, mod, pyc_output)
    mask = node.conversion & ASTFormattedValue.ConversionFlag.CONVERSION_MASK
    if mask == ASTFormattedValue.ConversionFlag.STR: pyc_output.write("!s")
    elif mask == ASTFormattedValue.ConversionFlag.REPR: pyc_output.write("!r")
    elif mask == ASTFormattedValue.ConversionFlag.ASCII: pyc_output.write("!a")
    if node.conversion & ASTFormattedValue.ConversionFlag.HAVE_FMT_SPEC:
        pyc_output.write(":")
        spec = node.format_spec.object.value.decode('utf-8', 'replace')
        pyc_output.write(spec)
    pyc_output.write("}")

def print_src(node: Optional[ASTNode], mod: PycModule, pyc_output: TextIO):
    global clean_build, cur_indent, F_STRING_QUOTE, in_lambda, print_docstring_and_globals, print_class_docstring

    if node is None:
        pyc_output.write("None")
        clean_build = True
        return

    t = getattr(node, 'type', None)

    if t in (ASTNodeType.NODE_BINARY, getattr(ASTNodeType, 'NODE_COMPARE', 999)):
        if t == getattr(ASTNodeType, 'NODE_COMPARE', 999):
            print_ordered(node, node.left, mod, pyc_output)
            cmp_strs = [" < ", " <= ", " == ", " != ", " > ", " >= ", " in ", " not in ", " is ", " is not ", " except ", " BAD "]
            op_str = cmp_strs[node.op] if hasattr(node, 'op') and 0 <= node.op < len(cmp_strs) else getattr(node, 'op_str', lambda: " ? ")()
            pyc_output.write(op_str)
            print_ordered(node, node.right, mod, pyc_output)
        else:
            print_ordered(node, node.left, mod, pyc_output)
            pyc_output.write(node.op_str())
            print_ordered(node, node.right, mod, pyc_output)

    elif t == ASTNodeType.NODE_UNARY:
        pyc_output.write(node.op_str())
        print_ordered(node, node.operand, mod, pyc_output)

    elif t == ASTNodeType.NODE_CALL:
        print_src(node.func, mod, pyc_output)
        pyc_output.write("(")
        first = True
        for param in node.pparams:
            if not first: pyc_output.write(", ")
            print_src(param, mod, pyc_output)
            first = False
        for key, val in node.kwparams:
            if not first: pyc_output.write(", ")
            if getattr(key, 'type', None) == ASTNodeType.NODE_NAME:
                pyc_output.write(key.name.value.decode('utf-8', 'replace'))
            else:
                pyc_output.write(key.object.value.decode('utf-8', 'replace'))
            pyc_output.write(" = ")
            print_src(val, mod, pyc_output)
            first = False
        if getattr(node, 'var', None) is not None:
            if not first: pyc_output.write(", ")
            pyc_output.write("*")
            print_src(node.var, mod, pyc_output)
            first = False
        if getattr(node, 'kw', None) is not None:
            if not first: pyc_output.write(", ")
            pyc_output.write("**")
            print_src(node.kw, mod, pyc_output)
            first = False
        pyc_output.write(")")

    elif t == ASTNodeType.NODE_DELETE:
        pyc_output.write("del ")
        print_src(node.value, mod, pyc_output)

    elif t == ASTNodeType.NODE_EXEC:
        pyc_output.write("exec ")
        print_src(node.statement, mod, pyc_output)
        if node.globals is not None:
            pyc_output.write(" in ")
            print_src(node.globals, mod, pyc_output)
            if node.locals is not None and node.globals != node.locals:
                pyc_output.write(", ")
                print_src(node.locals, mod, pyc_output)

    elif t == ASTNodeType.NODE_FORMATTEDVALUE:
        pyc_output.write(f"f{F_STRING_QUOTE}")
        print_formatted_value(node, mod, pyc_output)
        pyc_output.write(F_STRING_QUOTE)

    elif t == ASTNodeType.NODE_JOINEDSTR:
        pyc_output.write(f"f{F_STRING_QUOTE}")
        for val in node.values:
            if getattr(val, 'type', None) == ASTNodeType.NODE_FORMATTEDVALUE:
                print_formatted_value(val, mod, pyc_output)
            elif getattr(val, 'type', None) == ASTNodeType.NODE_OBJECT:
                val.object.print(pyc_output, mod, F_STRING_QUOTE)
            else:
                sys.stderr.write(f"Unsupported node type {getattr(val, 'type', None)} in NODE_JOINEDSTR\n")
        pyc_output.write(F_STRING_QUOTE)

    elif t == ASTNodeType.NODE_KEYWORD:
        pyc_output.write(node.word_str())

    elif t == ASTNodeType.NODE_LIST:
        pyc_output.write("[")
        first = True
        cur_indent += 1
        for val in node.values:
            if first: pyc_output.write("\n")
            else: pyc_output.write(",\n")
            start_line(cur_indent, pyc_output)
            print_src(val, mod, pyc_output)
            first = False
        cur_indent -= 1
        pyc_output.write("]")

    elif t == ASTNodeType.NODE_SET:
        pyc_output.write("{")
        first = True
        cur_indent += 1
        for val in node.values:
            if first: pyc_output.write("\n")
            else: pyc_output.write(",\n")
            start_line(cur_indent, pyc_output)
            print_src(val, mod, pyc_output)
            first = False
        cur_indent -= 1
        pyc_output.write("}")

    elif t == ASTNodeType.NODE_COMPREHENSION:
        pyc_output.write("[ ")
        print_src(node.result, mod, pyc_output)
        for gen in node.generators:
            pyc_output.write(" for ")
            print_src(gen.index, mod, pyc_output)
            pyc_output.write(" in ")
            print_src(gen.iter, mod, pyc_output)
            if gen.condition is not None:
                pyc_output.write(" if ")
                print_src(gen.condition, mod, pyc_output)
        pyc_output.write(" ]")

    elif t == ASTNodeType.NODE_MAP:
        pyc_output.write("{")
        first = True
        cur_indent += 1
        for key, val in node.values:
            if first: pyc_output.write("\n")
            else: pyc_output.write(",\n")
            start_line(cur_indent, pyc_output)
            print_src(key, mod, pyc_output)
            pyc_output.write(": ")
            print_src(val, mod, pyc_output)
            first = False
        cur_indent -= 1
        pyc_output.write(" }")

    elif t == ASTNodeType.NODE_CONST_MAP:
        keys = node.keys.object.values
        values = list(node.values)
        if hasattr(sys.modules[__name__], 'ASTMap'):
            temp_map = ASTMap()
            for key in keys:
                val = values.pop()
                temp_map.add(ASTObject(key), val)
            print_src(temp_map, mod, pyc_output)

    elif t == ASTNodeType.NODE_NAME:
        pyc_output.write(node.name.value.decode('utf-8', 'replace'))

    elif t == ASTNodeType.NODE_NODELIST:
        cur_indent += 1
        for ln in node.nodes:
            if getattr(ln, 'type', None) != ASTNodeType.NODE_NODELIST:
                start_line(cur_indent, pyc_output)
            print_src(ln, mod, pyc_output)
            end_line(pyc_output)
        cur_indent -= 1

    elif t == ASTNodeType.NODE_BLOCK:
        if node.blktype == ASTBlock.BlkType.BLK_ELSE and len(node.nodes) == 0:
            return
        if node.blktype == ASTBlock.BlkType.BLK_CONTAINER:
            end_line(pyc_output)
            print_block(node, mod, pyc_output)
            end_line(pyc_output)
            return

        pyc_output.write(node.type_str())
        if node.blktype in (ASTBlock.BlkType.BLK_IF, ASTBlock.BlkType.BLK_ELIF, ASTBlock.BlkType.BLK_WHILE):
            if node.negative: pyc_output.write(" not ")
            else: pyc_output.write(" ")
            print_src(node.cond, mod, pyc_output)
        elif node.blktype in (ASTBlock.BlkType.BLK_FOR, ASTBlock.BlkType.BLK_ASYNCFOR):
            pyc_output.write(" ")
            print_src(node.index, mod, pyc_output)
            pyc_output.write(" in ")
            print_src(node.iter, mod, pyc_output)
        elif node.blktype == ASTBlock.BlkType.BLK_EXCEPT and node.cond is not None:
            pyc_output.write(" ")
            print_src(node.cond, mod, pyc_output)
        elif node.blktype == ASTBlock.BlkType.BLK_WITH:
            pyc_output.write(" ")
            print_src(node.expr, mod, pyc_output)
            if node.var is not None:
                pyc_output.write(" as ")
                print_src(node.var, mod, pyc_output)

        pyc_output.write(":\n")
        cur_indent += 1
        print_block(node, mod, pyc_output)
        cur_indent -= 1

    elif t == ASTNodeType.NODE_OBJECT:
        obj = node.object
        if obj.type in (PycObjectType.TYPE_CODE, getattr(PycObjectType, 'TYPE_CODE2', 999)):
            decompyle(obj, mod, pyc_output)
        else:
            if hasattr(obj, 'value') and obj.value is not None and not isinstance(obj.value, (tuple, list, dict)):
                if isinstance(obj.value, bytes):
                    pyc_output.write(repr(obj.value.decode('utf-8', 'replace')))
                elif isinstance(obj.value, str):
                    pyc_output.write(repr(obj.value))
                else:
                    pyc_output.write(str(obj.value))
            elif getattr(obj, 'type', None) == getattr(PycObjectType, 'TYPE_NONE', None):
                pyc_output.write("None")
            else:
                try:
                    obj.print(pyc_output, mod)
                except Exception:
                    pass

    elif t == ASTNodeType.NODE_PRINT:
        pyc_output.write("print ")
        first = True
        if node.stream is not None:
            pyc_output.write(">>")
            print_src(node.stream, mod, pyc_output)
            first = False
        for val in node.values:
            if not first: pyc_output.write(", ")
            print_src(val, mod, pyc_output)
            first = False
        if not node.eol:
            pyc_output.write(",")

    elif t == ASTNodeType.NODE_RAISE:
        pyc_output.write("raise ")
        first = True
        for param in node.params:
            if not first: pyc_output.write(", ")
            print_src(param, mod, pyc_output)
            first = False

    elif t == ASTNodeType.NODE_RETURN:
        val = node.value
        if not in_lambda:
            if node.rettype == ASTReturn.RetType.RETURN: pyc_output.write("return ")
            elif node.rettype == ASTReturn.RetType.YIELD: pyc_output.write("yield ")
            elif node.rettype == ASTReturn.RetType.YIELD_FROM:
                if val is not None and getattr(val, 'type', None) == getattr(ASTNodeType, 'NODE_AWAITABLE', None):
                    pyc_output.write("await ")
                    val = val.expression
                else:
                    pyc_output.write("yield from ")
        print_src(val, mod, pyc_output)

    elif t == ASTNodeType.NODE_SLICE:
        if node.op & ASTSlice.SliceOp.SLICE1:
            print_src(node.left, mod, pyc_output)
        pyc_output.write(":")
        if node.op & ASTSlice.SliceOp.SLICE2:
            print_src(node.right, mod, pyc_output)

    elif t == ASTNodeType.NODE_IMPORT:
        if node.stores:
            if getattr(node.name, 'type', None) == ASTNodeType.NODE_IMPORT:
                pyc_output.write("from ")
                print_src(node.name.name, mod, pyc_output)
                pyc_output.write(" import ")
            elif is_equal_name(node.name, node.stores[0].src):
                pyc_output.write("import ")
                print_src(node.name, mod, pyc_output)
                src_bytes = get_name_bytes(node.name)
                dest_bytes = get_name_bytes(node.stores[0].dest)
                if src_bytes != dest_bytes:
                    if src_bytes and dest_bytes and src_bytes.startswith(dest_bytes + b'.'): pass
                    else:
                        pyc_output.write(" as ")
                        print_src(node.stores[0].dest, mod, pyc_output)
                return
            else:
                pyc_output.write("from ")
                print_src(node.name, mod, pyc_output)
                pyc_output.write(" import ")
            
            first = True
            for st in node.stores:
                if not first: pyc_output.write(", ")
                if getattr(st.src, 'type', None) == ASTNodeType.NODE_IMPORT: print_src(st.src.name, mod, pyc_output)
                else: print_src(st.src, mod, pyc_output)
                if not is_equal_name(st.src, st.dest):
                    pyc_output.write(" as ")
                    print_src(st.dest, mod, pyc_output)
                first = False
        else:
            pyc_output.write("import ")
            print_src(node.name, mod, pyc_output)

    elif t == ASTNodeType.NODE_FUNCTION:
        pyc_output.write("(lambda ")
        code_obj = node.code.object
        
        defargs = getattr(node, 'defargs', [])
        kwdefargs = getattr(node, 'kwdefargs', [])
        da_idx = 0
        narg = 0
        
        arg_count = getattr(code_obj, 'argCount', 0)
        for i in range(arg_count):
            if narg > 0: pyc_output.write(", ")
            pyc_output.write(code_obj.getLocal(narg).value.decode('utf-8', 'replace'))
            narg += 1
            if (arg_count - i) <= len(defargs):
                pyc_output.write(" = ")
                print_src(defargs[da_idx], mod, pyc_output)
                da_idx += 1
                
        kw_only_arg_count = getattr(code_obj, 'kwOnlyArgCount', 0)
        kw_da_idx = 0
        if kw_only_arg_count != 0:
            pyc_output.write("*" if narg == 0 else ", *")
            for i in range(kw_only_arg_count):
                pyc_output.write(", ")
                pyc_output.write(code_obj.getLocal(narg).value.decode('utf-8', 'replace'))
                narg += 1
                if (kw_only_arg_count - i) <= len(kwdefargs):
                    pyc_output.write(" = ")
                    print_src(kwdefargs[kw_da_idx], mod, pyc_output)
                    kw_da_idx += 1
        
        pyc_output.write(": ")
        prev_lambda = in_lambda
        in_lambda = True
        print_src(node.code, mod, pyc_output)
        in_lambda = prev_lambda
        pyc_output.write(")")

    elif t == ASTNodeType.NODE_STORE:
        src = node.src
        dest = node.dest
        
        if src is not None and getattr(src, 'type', None) == ASTNodeType.NODE_BINARY and getattr(src, 'inplace', False):
            print_src(src, mod, pyc_output)
            
        elif src is not None and getattr(src, 'type', None) == ASTNodeType.NODE_FUNCTION:
            code_src = src.code.object
            is_lambda = (code_src.name.value == b"<lambda>")
            
            pyc_output.write("\n")
            start_line(cur_indent, pyc_output)
            
            if is_lambda:
                print_src(dest, mod, pyc_output)
                pyc_output.write(" = lambda ")
            else:
                if hasattr(code_src, 'flags') and (code_src.flags & 0x80): pyc_output.write("async ")
                pyc_output.write("def ")
                print_src(dest, mod, pyc_output)
                pyc_output.write("(")

            defargs = getattr(src, 'defargs', [])
            kwdefargs = getattr(src, 'kwdefargs', [])
            da_idx = 0
            narg = 0
            
            arg_count = getattr(code_src, 'argCount', 0)
            for i in range(arg_count):
                if narg > 0: pyc_output.write(", ")
                pyc_output.write(code_src.getLocal(narg).value.decode('utf-8', 'replace'))
                narg += 1
                if (arg_count - i) <= len(defargs):
                    pyc_output.write(" = ")
                    print_src(defargs[da_idx], mod, pyc_output)
                    da_idx += 1
            
            kw_only_arg_count = getattr(code_src, 'kwOnlyArgCount', 0)
            kw_da_idx = 0
            if kw_only_arg_count != 0:
                pyc_output.write("*" if narg == 0 else ", *")
                for i in range(kw_only_arg_count):
                    pyc_output.write(", ")
                    pyc_output.write(code_src.getLocal(narg).value.decode('utf-8', 'replace'))
                    narg += 1
                    if (kw_only_arg_count - i) <= len(kwdefargs):
                        pyc_output.write(" = ")
                        print_src(kwdefargs[kw_da_idx], mod, pyc_output)
                        kw_da_idx += 1
                        
            flags = getattr(code_src, 'flags', 0)
            if flags & 0x04:
                if narg > 0: pyc_output.write(", ")
                pyc_output.write("*" + code_src.getLocal(narg).value.decode('utf-8', 'replace'))
                narg += 1
            if flags & 0x08:
                if narg > 0: pyc_output.write(", ")
                pyc_output.write("**" + code_src.getLocal(narg).value.decode('utf-8', 'replace'))
                narg += 1

            if is_lambda: pyc_output.write(": ")
            else:
                pyc_output.write("):\n")
                print_docstring_and_globals = True
            
            prev_lambda = in_lambda
            in_lambda = in_lambda or is_lambda
            print_src(src.code, mod, pyc_output)
            in_lambda = prev_lambda

        elif src is not None and getattr(src, 'type', None) == ASTNodeType.NODE_CLASS:
            pyc_output.write("\n")
            start_line(cur_indent, pyc_output)
            pyc_output.write("class ")
            print_src(dest, mod, pyc_output)
            
            bases = src.bases
            if bases and len(bases.values) > 0:
                pyc_output.write("(")
                first = True
                for val in bases.values:
                    if not first: pyc_output.write(", ")
                    print_src(val, mod, pyc_output)
                    first = False
                pyc_output.write("):\n")
            else:
                pyc_output.write(":\n")
            
            print_class_docstring = True
            
            class_body = None
            if getattr(src.code, 'type', None) == ASTNodeType.NODE_CALL:
                func_node = src.code.func
                class_body = getattr(func_node, 'code', func_node)
            
            if class_body: print_src(class_body, mod, pyc_output)
            else:
                start_line(cur_indent + 1, pyc_output)
                pyc_output.write("pass # <Decompilation Error: Class body missing>\n")
        else:
            print_src(dest, mod, pyc_output)
            pyc_output.write(" = ")
            print_src(src, mod, pyc_output)

    elif t == ASTNodeType.NODE_CHAINSTORE:
        for d in node.nodes:
            print_src(d, mod, pyc_output)
            pyc_output.write(" = ")
        print_src(node.src, mod, pyc_output)

    elif t == ASTNodeType.NODE_SUBSCR:
        print_src(node.name, mod, pyc_output)
        pyc_output.write("[")
        print_src(node.key, mod, pyc_output)
        pyc_output.write("]")
        
    elif t == getattr(ASTNodeType, 'NODE_CONVERT', 999):
        pyc_output.write("`")
        print_src(node.name, mod, pyc_output)
        pyc_output.write("`")

    elif t == ASTNodeType.NODE_TUPLE:
        if node.require_parens: pyc_output.write("(")
        first = True
        for val in node.values:
            if not first: pyc_output.write(", ")
            print_src(val, mod, pyc_output)
            first = False
        if len(node.values) == 1: pyc_output.write(",")
        if node.require_parens: pyc_output.write(")")
        
    elif t == getattr(ASTNodeType, 'NODE_ANNOTATED_VAR', 999):
        pyc_output.write(node.name.object.value.decode('utf-8', 'replace'))
        pyc_output.write(": ")
        print_src(node.annotation, mod, pyc_output)

    elif t == getattr(ASTNodeType, 'NODE_TERNARY', 999):
        print_src(node.if_expr, mod, pyc_output)
        pyc_output.write(" if ")
        if getattr(node.if_block, 'negative', False):
            pyc_output.write("not ")
        print_src(node.if_block.cond, mod, pyc_output)
        pyc_output.write(" else ")
        print_src(node.else_expr, mod, pyc_output)

    else:
        pyc_output.write(f"<NODE:{t}>")
        sys.stderr.write(f"Unsupported Node type: {t}\n")
        clean_build = False

    if t != getattr(ASTNodeType, 'NODE_INVALID', -1):
        clean_build = clean_build and True

def print_docstring(obj: PycObject, indent: int, mod: PycModule, pyc_output: TextIO) -> bool:
    if obj.type in (PycObjectType.TYPE_STRING, PycObjectType.TYPE_UNICODE):
        start_line(indent, pyc_output)
        obj.print(pyc_output, mod, True)
        pyc_output.write("\n")
        return True
    return False

def decompyle(code: PycCode, mod: PycModule, pyc_output: TextIO):
    global clean_build, print_class_docstring, print_docstring_and_globals, cur_indent

    source = build_from_code(code, mod)
    
    if clean_build:
        if source.nodes and getattr(source.nodes[0], 'type', None) == ASTNodeType.NODE_STORE:
            store = source.nodes[0]
            if (getattr(store.src, 'type', None) == ASTNodeType.NODE_NAME and 
                getattr(store.dest, 'type', None) == ASTNodeType.NODE_NAME):
                src_name = store.src.name.value
                dest_name = store.dest.name.value
                if src_name == b"__name__" and dest_name == b"__module__":
                    source.nodes.pop(0)

        if source.nodes and getattr(source.nodes[0], 'type', None) == ASTNodeType.NODE_STORE:
            store = source.nodes[0]
            if (getattr(store.src, 'type', None) == ASTNodeType.NODE_OBJECT and 
                getattr(store.dest, 'type', None) == ASTNodeType.NODE_NAME):
                dest_name = store.dest.name.value
                if dest_name == b"__qualname__":
                    source.nodes.pop(0)

        if (print_class_docstring and source.nodes and 
            getattr(source.nodes[0], 'type', None) == ASTNodeType.NODE_STORE):
            store = source.nodes[0]
            if (getattr(store.dest, 'type', None) == ASTNodeType.NODE_NAME and 
                store.dest.name.value == b"__doc__" and 
                getattr(store.src, 'type', None) == ASTNodeType.NODE_OBJECT):
                indent_adjustment = 0 if code.name.value == b"<module>" else 1
                if print_docstring(store.src.object, cur_indent + indent_adjustment, mod, pyc_output):
                    source.nodes.pop(0)

        if source.nodes and getattr(source.nodes[-1], 'type', None) == ASTNodeType.NODE_RETURN:
            ret = source.nodes[-1]
            val = ret.value
            remove_ret = False
            if val is None:
                remove_ret = True
            elif getattr(val, 'type', None) == ASTNodeType.NODE_LOCALS:
                remove_ret = True
            elif getattr(val, 'type', None) == ASTNodeType.NODE_OBJECT:
                if getattr(val.object, 'type', None) == getattr(PycObjectType, 'TYPE_NONE', None):
                    remove_ret = True
            if remove_ret:
                source.nodes.pop()

    if print_class_docstring:
        print_class_docstring = False

    if len(source.nodes) == 0:
        is_main_module = (code == getattr(mod, 'code', None))
        if not is_main_module:
            source.append(ASTKeyword(ASTKeyword.Word.KW_PASS))

    part1_clean = clean_build

    if print_docstring_and_globals:
        if code.consts.size > 0:
            print_docstring(code.getConst(0), cur_indent + 1, mod, pyc_output)

        if hasattr(code, 'getGlobals'):
            globs = code.getGlobals()
            if globs:
                start_line(cur_indent + 1, pyc_output)
                pyc_output.write("global ")
                first = True
                for glob in globs:
                    if not first:
                        pyc_output.write(", ")
                    pyc_output.write(glob.value.decode('utf-8', 'replace'))
                    first = False
                pyc_output.write("\n")
        print_docstring_and_globals = False

    print_src(source, mod, pyc_output)

    if not clean_build or not part1_clean:
        pyc_output.write("\n")
        start_line(cur_indent, pyc_output)
        pyc_output.write("# WARNING: Decompyle incomplete\n")