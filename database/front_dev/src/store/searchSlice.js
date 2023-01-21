import {createSlice} from "@reduxjs/toolkit"

const searchSlice = createSlice({
	name: 'search',
	initialState: {
		current: "",
	},
	reducers: {
		search: (state, action) => {
 			state.current = action.payload
		},
	},
})

export const {search} = searchSlice.actions

export default searchSlice.reducer
export const selectCurrentSearch = (state) => state.search.current