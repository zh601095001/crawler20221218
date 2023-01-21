import {createSlice} from "@reduxjs/toolkit"

const postSlice = createSlice({
	name: 'posts',
	initialState: {data: []},
	reducers: {
		setPosts: (state, action) => {
			state.data = action.payload
		},
		deletePost:(state,action)=>{
			const {postId} = action.payload
			state.data = state.data.filter(post=>{
				return post.postId !== postId;
			})
		}
	},
})

export const {setPosts,deletePost} = postSlice.actions

export default postSlice.reducer

export const selectPosts = state => state.posts.data
