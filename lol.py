pytest = """# dimitri was here
import this"""
with open('hi.py', 'w') as fo:
    fo.write(pytest)
import hi