import axios from "axios"
import { useEffect, useState } from "react"
import API_BASE_URL from "../api"
import { useNavigate } from "react-router-dom"

export default function HomeEl() {
  const [loading, isLoading] = useState(false)
  const [workouts, setWorkouts] = useState([])
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

  if (loading)
    return <h1>Loading...</h1>

  return (
    <div>
      <h1>Workout Page</h1>
      {workouts.map((workout) => (
        <div className="mb-5 p-5 bg-green-800 text-white cursor-pointer" onClick={() => handleClick(workout.id)} key={workout.id}>
          <h3>{workout.name}</h3>
          <h3>{workout.notes || "Nothing"}</h3>
        </div>
      ))}
    </div>
  )
}
