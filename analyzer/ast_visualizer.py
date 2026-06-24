class ASTVisualizer:
    """
    Simplifies the pyjsparser AST into a clean structure for frontend visualization.
    """

    @staticmethod
    def simplify_ast(node, max_depth=5, current_depth=0):
        """
        Recursively simplifies the AST node for visualization.
        Stops at max_depth to prevent the tree from becoming too large.
        """
        if not node or not isinstance(node, dict) or current_depth > max_depth:
            return None

        node_type = node.get("type", "Unknown")
        simplified = {
            "name": node_type,
            "children": []
        }

        # Add specific details based on node type
        if node_type in ("FunctionDeclaration", "FunctionExpression", "ArrowFunctionExpression"):
            if node.get("id") and node["id"].get("name"):
                simplified["name"] = f"FunctionDef: {node['id']['name']}"
            else:
                simplified["name"] = "FunctionDef"
                
            params = node.get("params", [])
            if params:
                simplified["children"].append({
                    "name": f"arguments ({len(params)} params)"
                })
            
            body = node.get("body")
            if body:
                body_child = ASTVisualizer.simplify_ast(body, max_depth, current_depth + 1)
                if body_child:
                    body_child["name"] = "body"
                    simplified["children"].append(body_child)

        elif node_type == "BlockStatement":
            for stmt in node.get("body", []):
                child = ASTVisualizer.simplify_ast(stmt, max_depth, current_depth + 1)
                if child:
                    simplified["children"].append(child)

        elif node_type == "IfStatement":
            simplified["name"] = "If"
            consequent = node.get("consequent")
            if consequent:
                child = ASTVisualizer.simplify_ast(consequent, max_depth, current_depth + 1)
                if child:
                    simplified["children"].append(child)

        elif node_type == "CallExpression":
            callee_name = "unknown"
            callee = node.get("callee", {})
            if callee.get("type") == "Identifier":
                callee_name = callee.get("name")
            elif callee.get("type") == "MemberExpression":
                prop = callee.get("property", {})
                if prop.get("type") == "Identifier":
                    callee_name = prop.get("name")
            
            simplified["name"] = f"Expr (Call): {callee_name}"

        elif node_type == "Program":
            simplified["name"] = "Module"
            for stmt in node.get("body", []):
                child = ASTVisualizer.simplify_ast(stmt, max_depth, current_depth + 1)
                if child:
                    simplified["children"].append(child)
        
        else:
            # Try to fetch generic children for other statements
            for key in ["body", "consequent", "alternate", "declarations"]:
                val = node.get(key)
                if isinstance(val, list):
                    for item in val:
                        child = ASTVisualizer.simplify_ast(item, max_depth, current_depth + 1)
                        if child:
                            simplified["children"].append(child)
                elif isinstance(val, dict):
                    child = ASTVisualizer.simplify_ast(val, max_depth, current_depth + 1)
                    if child:
                        simplified["children"].append(child)

        # Clean up empty children arrays
        if not simplified["children"]:
            del simplified["children"]

        return simplified
