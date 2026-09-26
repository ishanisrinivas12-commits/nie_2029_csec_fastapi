import { useState } from "react"

export default function Square(){
    const [num1, setNum1] = useState(0)
    const [num2, setnum2] = useState(0)
    const [sum, setSum] = useState(0)
    return(
        <>
             <p>Number 1: <input type="text"
             value ={num1} onChange={(e) => {setNum1(parseInt(e.target.value))}}/></p>
             <p>Number 2: <input type="text"
             value ={num2} onChange={(e) => {setnum2(parseInt(e.target.value))}}/></p>
             <p><button onClick={ () => {setSum(num1 + num2);}}>Calculate Sum</button></p>
             <p>Sum of {num1} and {num2} is {sum}</p>
        </>
    )
}