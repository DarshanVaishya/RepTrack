import axios from "axios";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import API_BASE_URL from "../api";

export default function WorkoutEl() {
  const { workout_id } = useParams();
  const [workout, setWorkout] = useState(null)

  useEffect(() => {
    axios.get(`${API_BASE_URL}/workout/${workout_id}`).then(response => {
      setWorkout(response.data.data)
      console.log(response.data.data)
    })
  }, [])

  if (workout == null)
    return <h1>Loading...</h1>

  return (
    <div>
      <h1 className="mb-1 text-2xl font-semibold">{workout.name}</h1>
      {workout.notes && <h2>Notes: {workout.notes}</h2>}

      <h3>Exercises:</h3>
      {!workout.workout_exercises ? <p>No exercises for this workout.</p> :
        workout.workout_exercises.map(exercise => <div className="py-2 bg-neutral-200" key={exercise.id}>
          <p>Exercise: {exercise.exercise.name}</p>
          <p>Notes: {exercise.notes && exercise.notes}</p>
          <p>Sets:</p>
          {
            exercise.sets.map(set => <div key={set.id}>
              <div className="flex gap-5">
                <span>{set.order_index}</span>
                <span>Reps: {set.reps}</span>
                <span>Weight: {set.weight}</span>
                <span className="capitalize">{set.set_type}</span>
              </div>
            </div>)
          }
        </div>)
      }
    </div >
  );
}
