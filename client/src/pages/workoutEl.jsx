import axios from "axios";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import API_BASE_URL from "../api";

export default function WorkoutEl() {
  const { workout_id } = useParams();
  const [workout, setWorkout] = useState(null)
  const [exercises, setExercises] = useState(null)

  const [exercise_id, setExerciseId] = useState()
  const [order_index, setOrderIdx] = useState()
  const [notes, setNotes] = useState("")

  const [reps, setReps] = useState()
  const [weight, setWeight] = useState()
  const [set_type, setSetType] = useState()

  useEffect(() => {
    axios.get(`${API_BASE_URL}/workout/${workout_id}`).then(response => {
      setWorkout(response.data.data)
    })

    axios.get(`${API_BASE_URL}/exercises`).then(response => {
      setExercises(response.data.data)
    })
  }, [])

  const handleExerciseSubmit = async e => {
    e.preventDefault()
    await axios.post(`${API_BASE_URL}/workout/${workout_id}/exercise`, {
      exercise_id,
      order_index,
      notes,
      workout_id
    })
  }

  const handleSetSubmit = async e => {
    e.preventDefault()
    const response = await axios.post(`${API_BASE_URL}/workout/${workout_id}/exercise/${exercise_id}/set`, {
      reps,
      weight,
      set_type,
      order_index,
      notes
    })
  }

  if (workout == null)
    return <h1>Loading...</h1>

  return (
    <div>
      <h1 className="mb-1 text-2xl font-semibold">{workout.name}</h1>
      {workout.notes && <h2>Notes: {workout.notes}</h2>}

      <h3>Workout Exercises:</h3>
      {!workout.workout_exercises ? <p>No exercises for this workout.</p> :
        workout.workout_exercises.map(exercise => <div className="py-2 bg-neutral-200 my-2" key={exercise.id}>
          <p>{exercise.id} {exercise.exercise.name}</p>
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

      <h3 className="mt-5 text-2xl">Add a workout exercise</h3>
      <form onSubmit={e => handleExerciseSubmit(e)}>
        <input type="number" placeholder="exercise id" value={exercise_id} onChange={e => setExerciseId(e.target.value)} />
        <input type="number" placeholder="order index" value={order_index} onChange={e => setOrderIdx(e.target.value)} />
        <input type="text" placeholder="notes" value={notes} onChange={e => setNotes(e.target.value)} />
        <button type="submit">Add</button>
      </form>

      <h3 className="mt-5 text-2xl">Add a workout set</h3>
      <form onSubmit={e => handleSetSubmit(e)}>
        <input type="number" placeholder="exercise id" value={exercise_id} onChange={e => setExerciseId(e.target.value)} />
        <input type="number" placeholder="Reps" value={reps} onChange={e => setReps(e.target.value)} />
        <input type="number" placeholder="Weight" value={weight} onChange={e => setWeight(e.target.value)} />
        <input type="text" placeholder="set type" value={set_type} onChange={e => setSetType(e.target.value)} />
        <input type="number" placeholder="order index" value={order_index} onChange={e => setOrderIdx(e.target.value)} />
        <input type="text" placeholder="notes" value={notes} onChange={e => setNotes(e.target.value)} />
        <button type="submit">Add</button>
      </form>

      <h3 className="mt-5 text-2xl">All Exercises</h3>
      {exercises.map(exercise => <div key={exercise.id}>
        <h4>{exercise.id} {exercise.name}</h4>
      </div>)}
    </div >
  );
}
