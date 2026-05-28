def eval_rpn_12(tokens):
    stack = []
    for token in tokens:
        if token in '+-*':
            b = stack.pop()
            a = stack.pop()
            if token == '+':
                stack.append(a + b)
            elif token == '-':
                stack.append(a - b)
            else:
                stack.append(a * b)
        else:
            stack.append(int(token))
    return stack[-1]
