class A{
    // [Symbol.toStringTag] = "A"
    constructor(arg1) {
        this.arg1 = arg1
        // this[Symbol.toStringTag] = "A"
    }
    log(){
        console.log(this.arg1)
    }
}
let a = new A()
a.log()
console.log(Object.prototype.toString.call(a));
