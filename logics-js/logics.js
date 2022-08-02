import LogicsParser from "./parser.js";

/** Wrapper for JavaScript values in the Logics VM, emulating
 * Python-style values and JSON-serializable objects. */
export class Value {
    #value;  // private property: The native value
    #type;  // private property: Logics type name

    constructor(value) {
        if (value instanceof Value) {
            this.#value = value.valueOf();
            this.#type = value.type();
        }
        else {
            this.#value = value;
            this.#type = this.constructor.type(value);
        }
    }

    /// Return value's native JS value
    valueOf() {
        return this.#value;
    }

    /// Returns the Logics value type; The type is cached in this.#type, for further usage.
    type() {
        return this.#type || (this.#type = this.constructor.type(this.#value))
    }

    /// Determine Logics value type from a JavaScript native value
    static type(value) {
        switch (typeof value) {
            case "undefined":
                return "NoneType";

            case "boolean":
                return "bool";

            case "number":
                if (value % 1 === 0) {
                    return "int";
                }

                return "float";

            case "string":
                return "str";

            case "object":
                // Check if every item of the array has a valid Logics type.
                if (value instanceof Array) {
                    for (let item of value) {
                        if (!this.type(item)) {
                            throw new Error("Cannot fully convert Array into a valid Logics type");
                        }
                    }

                    return "list";
                }
                else if (value === null) {
                    return "NoneType";
                }

                // Check if every property of the object has a valid Logics type.
                for (let key of Object.keys(value)) {
                    if (!this.type(value[key])) {
                        throw new Error("Cannot fully convert Object into a valid Logics type");
                    }
                }

                return "dict";
        }
    }

    /// Return the value's representation
    repr() {
        switch (this.type()) {
            case "NoneType":
                return "None";

            case "bool":
                return this.#value ? "True" : "False";

            case "int":
            case "float":
                return this.#value.toString();

            case "str":
                return "\"" + this.#value.toString().replace("\"", "\\\"") + "\"";

            case "list":
               return "[" +
                    this.#value.map(
                        item => {
                            if (!( item instanceof Value )) {
                                item = new Value(item);
                            }

                            return item.repr()
                        }
                    ).join(", ") + "]";

            case "dict":
                return "{" +
                    Object.keys(this.#value).map(
                        key => {
                            if (!( key instanceof Value)) {
                                key = new Value(key);
                            }

                            let value = this.#value[key];
                            if (!(value instanceof Value)) {
                                value = new Value(value);
                            }

                            return key + ": " + value.repr()
                        }
                    ).join(", ") + "}";

            default:
                throw new Error("Unimplemented repr for " + this.type());
        }
    }

    /**
     * Convert Value as Logics string representation.
     */
    toString() {
        switch (this.type()) {
            case "str":
            case "float":
            case "int":
                return this.#value.toString();

            default:
                return this.repr();
        }
    }

    // Returns JS-native boolean value.
    toBool() {
        return Boolean(this.#value);
    }

    // Returns JS-native int value.
    toInt() {
        if (this.#value === true) {
            return 1;
        }

        return parseInt(this.#value) || 0;
    }

    // Returns JS-native float value.
    toFloat() {
        if (this.#value === true) {
            return 1.0;
        }

        return parseFloat(this.#value) || 0.0;
    }

    // Returns JS-native list value.
    toList() {
        let type = this.type();

        if (type === "list") {
            return this.#value;
        }
        else if (type) {
            return [this.#value];
        }

        return null;
    }

    // Returns JS-native dict value.
    toDict() {
        let type = this.type();

        if (type === "dict") {
            return this.#value;
        }
        else if (type) {
            let dict = {};
            dict[this.#value] = this.#value;
            return dict;
        }

        return null;
    }

    // Get index
    __getitem__(index) {
        if( this.type() === "dict" ) {
            return new Value(this.#value[index.toString()]);
        }
        else if( this.type() === "list" || this.type() === "str" ) {
            return new Value(this.#value[index.toInt()]);
        }

        return new Value(null);
    }

    // Checks if a given value is part of another value
    __in__(value) {
        if (value.type() === "dict") {
            return value.valueOf()[this.toString()] !== undefined;
        }
        else if (value.type() === "list") {
            // We need to compare every item using __cmp__()
            for(let item of value.valueOf()) {
                item = new Value(item);
                if(item.__cmp__(this) === "eq") {
                    return true;
                }
            }

            return false;
            //return new Value(value.valueOf().indexOf(this.valueOf()) >= 0);
        }

        return value.toString().indexOf(this.toString()) >= 0;
    }

    // Compare
    __cmp__(other) {
        let a, b;

        // Dict types
        if (this.type() === "dict" || other.type() === "dict") {
            a = this.toDict();
            b = other.toDict();

            let ak = Object.keys(a);
            let bk = Object.keys(b);

            if (ak.length < bk.length) {
                return -1;
            }
            else if (ak.length > bk.length) {
                return 1;
            }

            for( let k of ak ) {
                if( typeof b[k] === "undefined" ) {
                    return 1;
                }

                let av = new Value(a[k]);
                let bv = new Value(b[k]);

                let res;
                if ((res = av.__cmp__(bv)) !== 0) {
                    return res;
                }
            }

            return 0;
        }
        // List types
        else if (this.type() === "list" || other.type() === "list") {
            a = this.toList();
            b = other.toList();

            if (a.length < b.length) {
                return -1;
            }
            else if (a.length > b.length) {
                return 1;
            }

            for(let i = 0; i < a.length; i++) {
                let av = new Value(a[i]);
                let bv = new Value(b[i]);

                let res;
                if ((res = av.__cmp__(bv)) !== 0) {
                    return res;
                }
            }

            return 0;
        }
        // Other types
        else if (this.type() === "str" || other.type() === "str") {
            a = this.toString();
            b = other.toString();
        }
        else if (this.type() === "float" || other.type() === "float") {
            a = this.toFloat();
            b = other.toFloat();
        }
        else {
            a = this.toInt();
            b = other.toInt();
        }

        // Perform final comparison
        if (a < b) {
            return -1;
        }
        else if (a > b) {
            return 1;
        }

        return 0;
    }

    // Performs an add-operation with another Value object.
    __add__(op) {
        if( this.type() === "str" || op.type() === "str" ) {
            return new Value(this.toString() + op.toString());
        }

        if( this.type() === "float" || op.type() === "float" ) {
            return new Value(this.toFloat() + op.toFloat());
        }

        return new Value(this.toInt() + op.toInt());
    }

    // Performs a sub-operation with another Value object.
    __sub__(op) {
        if( this.type() === "float" || op.type() === "float" ) {
            return new Value(this.toFloat() - op.toFloat());
        }

        return new Value(this.toInt() - op.toInt());
    }

    // Performs a mul-operation with another Value object.
    __mul__(op) {
        if (this.type() === "str") {
            return new Value(this.toString().repeat(op.toInt()));
        }
        else if (op.type() === "str") {
            return new Value(op.toString().repeat(this.toInt()));
        }

        if( this.type() === "float" || op.type() === "float" ) {
            return new Value(this.toFloat() * op.toFloat());
        }

        return new Value(this.toInt() * op.toInt());
    }

    // Performs a div-operation with another Value object.
    __div__(op) {
        if( this.type() === "float" || op.type() === "float" ) {
            return new Value(this.toFloat() / op.toFloat());
        }

        return new Value(this.toInt() / op.toInt());
    }

    // Performs a mod-operation with another Value object.
    __mod__(op) {
        if( this.type() === "float" || op.type() === "float" ) {
            return new Value(this.toFloat() % op.toFloat());
        }

        return new Value(this.toInt() % op.toInt());
    }

    // Performs a mod-operation with another Value object.
    __pow__(op) {
        if( this.type() === "float" || op.type() === "float" ) {
            return new Value(this.toFloat() ** op.toFloat());
        }

        return new Value(this.toInt() ** op.toInt());
    }

    // Performs unary plus
    __pos__() {
       if (this.type() === "float") {
           return new Value(+this.toFloat());
       }

       return new Value(+this.toInt());
    }

    // Performs unary minus
    __neg__() {
       if (this.type() === "float") {
           return new Value(-this.toFloat());
       }

       return new Value(-this.toInt());
    }

    // Performs unary complement
    __invert__() {
       return new Value(~this.toInt());
    }
}

/** The Logics VM in JavaScript */
export default class Logics {
    static #parser = new LogicsParser();

    /** Create a new VM with a given piece of code. */
    constructor(src) {
        this.ast = this.constructor.#parser.parse(src);
        this.ast.dump();
        this.functions = {};
    }

    /** Run the VM with a given set of values.
     * Returns the topmost value of the stack, if any. */
    run(values) {
        let stack = [];

        // Push a guaranteed Value
        stack.op0 = function(value) {
            if( !( value instanceof Value ) ){
                value = new Value(value);
            }

            this.push(value);
        }

        // Perform stack operation with one operand
        stack.op1 = function(fn) {
            this.op0(fn(this.pop()));
        }

        // Perform stack operation with two operands
        stack.op2 = function(fn) {
            let b = this.pop();
            this.op0(fn(this.pop(), b));
        }

        this.traverse(this.ast, stack, values || {});
        return stack.pop();
    }

    /**
     * General traversal function.
     *
     * This function performs pre, loop or pass and post operations.
     * @param node
     * @param stack
     * @param values
     */
    traverse(node, stack, values) {
        // This helper function simulates a match-statement like in Rust or Python...
        function action(key, object) {
            let fn;

            if ((fn = object[key]) !== undefined) {
                return fn() ?? true;
            }

            // Rust-like '_' wildcard fallback
            if ((fn = object["_"]) !== undefined) {
                return fn();
            }

            return false;
        }

        // Flow operations
        if (!action(node.emit, {
                "comprehension": () => {
                    console.assert(node.children.length === 3 || node.children.length === 4);
                    this.traverse(node.children[2], stack, values);

                    // obtain the list
                    let list = stack.pop().toList().valueOf();

                    let ret = [];

                    // iterate over list
                    for( let i of list ) {
                        values[node.children[1].match] = i;
                        this.traverse(node.children[0], stack, values);

                        // optional if
                        if (node.children.length === 4) {
                            this.traverse(node.children[3], stack, values);
                            if (!stack.pop().toBool()) {
                                continue;
                            }
                        }
                        ret.push(stack.pop());
                    }

                    // push result list
                    stack.op0(ret);
                },
                "and": () => {
                    console.assert(node.children.length === 2);
                    this.traverse(node.children[0], stack, values);

                    let check = stack.pop();
                    if (check.toBool()) {
                        this.traverse(node.children[1], stack, values);
                    }
                    else {
                        stack.push(check);
                    }
                },
                "if": () => {
                    console.assert(node.children.length === 3);

                    // Evaluate condition
                    this.traverse(node.children[1], stack, values);

                    // Evaluate specific branch
                    if (stack.pop().toBool()) {
                        this.traverse(node.children[0], stack, values);
                    } else {
                        this.traverse(node.children[2], stack, values);
                    }
                },
                "or": () => {
                    console.assert(node.children.length === 2);
                    this.traverse(node.children[0], stack, values);

                    let check = stack.pop();
                    if (!check.toBool()) {
                        this.traverse(node.children[1], stack, values);
                    }
                    else {
                        stack.push(check);
                    }
                },
                "cmp": () => {
                    for (let i = 0; i < node.children.length; i++) {
                        this.traverse(node.children[i], stack, values);

                        if (i === 0) {
                            continue;
                        }

                        let b = stack.pop();
                        let a = stack.pop();

                        let res = action(node.children[i].emit, {
                            "eq": () => a.__cmp__(b) === 0,
                            "gteq": () => a.__cmp__(b) >= 0,
                            "gt": () => a.__cmp__(b) > 0,
                            "lteq": () => a.__cmp__(b) <= 0,
                            "lt": () => a.__cmp__(b) < 0,
                            "neq": () => a.__cmp__(b) !== 0,
                            "_": () => console.log("unreachable"),
                        });

                        // Either push false and break or push b
                        stack.op0(res ? i === node.children.length - 1 ? true : b : false);

                        if (!res) {
                            break;
                        }
                    }
                }
            })) {

            if (node.children !== undefined) {
                // Iterate over children
                for (let child of node.children) {
                    this.traverse(child, stack, values);
                }
            }
        }

        // Stack operations
        return action(node.emit, {
            "False": () => stack.op0(false),
            "Identifier": () => {
                let name = node.match;

                if (name in values) {
                    stack.push(new Value(values[name]));
                }
                else if (name in this.functions) {
                    stack.push(new Value(this.functions[name]));
                }
                else {
                    stack.push(new Value(null));
                }
            },
            "None": () => stack.op0(null),
            "Number": () => stack.op0(parseFloat(node.match)),
            "String": () => stack.op0(node.match.substring(1, node.match.length - 1)), // cut "..." from string.
            "True": () => stack.op0(true),

            "add": () => stack.op2((a, b) => a.__add__(b)),
            "div": () => stack.op2((a, b) => a.__div__(b)),
            "in": () => stack.op2((a, b) => a.__in__(b)),
            "invert": () => stack.op1((a) => a.__invert__()),
            "list": () => stack.op0(stack.splice(-node.children.length).map(item => item.valueOf())),
            "mod": () => stack.op2((a, b) => a.__mod__(b)),
            "mul": () => stack.op2((a, b) => a.__mul__(b)),
            "neg": () => stack.op1((a) => a.__neg__()),
            "not": () => stack.op1((a) => !a.toBool()),
            "outer": () => stack.op2((a, b) => !a.__in__(b)),
            "pos": () => stack.op1((a) => a.__pos__()),
            "pow": () => stack.op2((a, b) => a.__pow__(b)),
            "strings": () => stack.op0(stack.splice(-node.children.length).join("")),
            "sub": () => stack.op2((a, b) => a.__sub__(b)),
        });
    }
}

// Register Logics in the browser
if (window !== undefined) {
    window.Logics = Logics;
}
