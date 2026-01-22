import axios from "axios"
import { useEffect, useState } from "react"
import API_BASE_URL from "../api"
import { useNavigate } from "react-router-dom"

export default function HomeEl() {
  const [loading, isLoading] = useState(false)
  const [workouts, setWorkouts] = useState([])
  const [name, setName] = useState("")
  const [notes, setNotes] = useState("")
  const navigate = useNavigate()

  useEffect(() => {
    isLoading(true)
    axios.get(`${API_BASE_URL}/workout`).then(response => {
      setWorkouts(response.data.data)
    }).finally(() => isLoading(false))
  }, [])

  const handleClick = (id) => {
    navigate(`/workouts/${id}`)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const response = await axios.post(`${API_BASE_URL}/workout`, {
      name,
      notes
    })

    console.log(response.data.data)
    const workout = response.data.data
    setWorkouts([...workouts, workout])
  }

  const handleDelete = async id => {
    const response = axios.delete(`${API_BASE_URL}/workout/${id}`)
    console.log("DELETED")
    console.log(response.data)

    const newWorkouts = workouts.filter(workout => workout.id !== id)
    setWorkouts(newWorkouts)
  }

  if (loading)
    return <h1>Loading...</h1>

  return (
    <div>
      <h2 className="text-2xl mb-2">Create a workout</h2>
      <form className="mb-5" onSubmit={e => handleSubmit(e)}>
        <div>
          <label>Name</label>
          <input type="text" value={name} onChange={e => setName(e.target.value)} />
        </div>

        <div>
          <label>Notes</label>
          <input type="text" value={notes} onChange={e => setNotes(e.target.value)} />
        </div>
        <button type="submit">Create workout</button>
      </form>

      <h1 className="text-3xl mb-2">Workouts</h1>
      {workouts.map((workout) => (
        <div className="flex justify-between mb-5 p-5 bg-green-800 text-white cursor-pointer" onClick={() => handleClick(workout.id)} key={workout.id}>
          <div>
            <h3>{workout.name}</h3>
            <h3>{workout.notes && workout.notes}</h3>
          </div>
          <button onClick={e => {
            e.stopPropagation()
            handleDelete(workout.id)
          }}>Delete</button>
        </div>
      ))}

    </div>
  )
}
