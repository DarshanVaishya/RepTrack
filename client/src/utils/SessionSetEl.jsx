import axios from "axios"
import { useState } from "react"
import API_BASE_URL from "../api"

export default function SessionSetEl({ set, session_id }) {
  const [reps, setReps] = useState("")
  const [weight, setWeight] = useState("")

  const handleCompleteSet = async (e) => {
    e.preventDefault()
    const response = await axios.put(`${API_BASE_URL}/sessions/${session_id}/set/${set.id}`, {
      actual_reps: reps,
      actual_weight: weight,
      notes: ""
    })

    console.log("Set complete", response.data.data)
  }

  return (
    <form className="flex gap-1" onSubmit={e => handleCompleteSet(e)}>
      <span>Reps:
        {
          set.actual_reps ? set.actual_reps :
            <input
              className="w-10 text-center"
              placeholder={set.planned_reps}
              value={reps}
              onChange={(e) => setReps(e.target.value)}
              type="number"
              required
            />
        }
      </span>

      <span>Weight:
        {
          set.actual_weight ? set.actual_weight :
            <input
              className="w-10 text-center"
              placeholder={set.planned_weight}
              value={weight}
              onChange={(e) => setWeight(e.target.value)}
              type="number"
              required
            />
        }
      </span>
      {!set.actual_reps && !set.actual_weight && <button type="submit">complete</button>}
    </form>
  )
}
