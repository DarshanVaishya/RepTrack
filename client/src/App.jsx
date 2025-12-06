import { useState } from 'react'
import './index.css'

function App() {
	const [count, setCount] = useState(0)

	return (
		<div className='container mx-auto'>
			<div>
				<button className="bg-amber-300 p-5 rounded hover:bg-amber-500 transition-colors" onClick={() => setCount((count) => count + 1)}>
					count is {count}
				</button>
				<p>
					Edit <code>src/App.jsx</code> and save to test HMR
				</p>
			</div>
			<p className="read-the-docs">
				Click on the Vite and React logos to learn more
			</p>
		</div>
	)
}

export default App
