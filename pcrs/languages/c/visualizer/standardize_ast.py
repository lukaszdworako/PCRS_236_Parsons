from pycparser import c_ast


class NormalizeWalker(c_ast.NodeVisitor):
    def visit_If(self, node):
        if node.iftrue:
            if not isinstance(node.iftrue, c_ast.Compound):
                node.iftrue = c_ast.Compound([node.iftrue])

        if node.iffalse:
            if not isinstance(node.iffalse, c_ast.Compound):
                node.iffalse = c_ast.Compound([node.iffalse])

        for (child_type, child_node) in node.children():
            self.visit(child_node)


    def visit_While(self, node):
        if not isinstance(node.stmt, c_ast.Compound):
            node.stmt = c_ast.Compound([node.stmt])

        for (child_type, child_node) in node.children():
            self.visit(child_node)


    # TODO: implement doWhile
    def visit_DoWhile(self, node):
        if not isinstance(node.stmt, c_ast.Compound):
            node.stmt = c_ast.Compound([node.stmt])

        for (child_type, child_node) in node.children():
            self.visit(child_node)


    def visit_For(self, node):
        if not isinstance(node.stmt, c_ast.Compound):
            node.stmt = c_ast.Compound([node.stmt])

        # TODO: ExprList in "init" or "next"
        # for (int i = 0; i < 5; i++, g--)
        for (child_type, child_node) in node.children():
            self.visit(child_node)

    def visit_Struct(self, node):
        raise NotImplementedError("Structs are not yet supported")
