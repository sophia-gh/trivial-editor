

export async function run(userCode){
    try{
        const response = await fetch('http://127.0.0.1:5000/run',{
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({code: userCode}),
        })

        if(!response.ok){

            const error = await response.json()
            throw new Error(error.error);
        }

        const {result} = await response.json();
        return result;

    } catch(err){
        throw new Error(`Error running code: ${err.message}`);
    }
}
