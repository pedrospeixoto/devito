from devito.logger import warning
from devito.operator import Operator
from devito.ir.iet.visitors import FindNodes
from devito.ir.iet.nodes import Expression
from devito.ops.node_factory import OPSNodeFactory
from devito.ops.transformer import make_ops_ast

__all__ = ['OperatorOPS']


class OperatorOPS(Operator):

    """
    A special Operator generating and executing OPS code.
    """

    def _specialize_iet(self, iet, **kwargs):

        warning("The OPS backend is still work-in-progress")

        # EVERYTHING BELLOW IS TEMPORARY FOR EAGE PAPER

        expressions = [i for i in FindNodes(Expression).visit(iet)]
        

        # OPS nodes factory.
        nfops = OPSNodeFactory()

        for expression in expressions:
            ops_expr = make_ops_ast(expression.expr, nfops)
            warning(expression)
            print(ops_expr)

        return iet
