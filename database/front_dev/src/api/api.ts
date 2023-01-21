// Import the RTK Query methods from the React-specific entry point
import {BaseQueryApi} from '@reduxjs/toolkit/dist/query/baseQueryTypes'
import {createApi, FetchArgs, fetchBaseQuery} from '@reduxjs/toolkit/query/react'
import {message} from "antd"

const baseQuery = fetchBaseQuery({
    baseUrl: '/',
    credentials: 'include',
    prepareHeaders: (headers, {getState}) => {
        // @ts-ignore
        return headers
    }
})

const baseQueryWithReauth = async (args: string | FetchArgs, api: BaseQueryApi, extraOptions: {}) => {
    let result = await baseQuery(args, api, extraOptions)

    // @ts-ignore
    if (result?.error?.originalStatus > 300) {
        // send refresh token to get new access token
        console.log(result)
        // @ts-ignore
        message.error(result.error.error)
    }


    return result
}

export const api = createApi({
    reducerPath: 'api',
    baseQuery: baseQueryWithReauth,
    tagTypes: ['MatchSettings'],
    endpoints: builder => ({
        getAllMatchNames: builder.mutation({
            query: (dateRange) => ({
                url: `/analysis/matches?dateRange=${dateRange}`,
                method: "GET"
            }),
        }),
        analysisMatched: builder.mutation({
            query: ({body, dateRange}) => ({
                url: `/analysis/matches?dateRange=${dateRange}`,
                method: "POST",
                body
            })
        }),
        setEmail: builder.mutation({
            query: (body) => ({
                url: `/settings?collection=settings`,
                method: "POST",
                body
            })
        }),
        getSettings: builder.mutation({
            query: () => ({
                url: `/settings?collection=settings`,
                method: "GET",
            })
        }),
        getMatchSettings: builder.mutation({
            query: (body) => ({
                url: `/settings/s?collection=settings`,
                method: "POST",
                body,
                providesTags: ["MatchSettings"]
            }),
        }),
        setMatchSettings: builder.mutation({
            query: (body) => ({
                url: `/settings?collection=settings`,
                method: "PUT",
                body
            })
        }),
        deleteMatchSettings: builder.mutation({
            query: (body) => ({
                url: `/settings?collection=settings`,
                method: "DELETE",
                body
            }),
            invalidatesTags: ["MatchSettings"]
        }),
    })
})

// Export the auto-generated hook for the endpoint
// 使用方法：
// const [modify,{isLoading,isFetching,error}] = useModifyMutation()
// const {data, isFetching} = useGetQuery()
export const {
    useGetAllMatchNamesMutation,
    useAnalysisMatchedMutation,
    useSetEmailMutation,
    useGetSettingsMutation,
    useGetMatchSettingsMutation,
    useSetMatchSettingsMutation,
    useDeleteMatchSettingsMutation
} = api

// @ts-ignore
// export const selectPostsQuery = createSelector(selectPosts,res=>res.data)