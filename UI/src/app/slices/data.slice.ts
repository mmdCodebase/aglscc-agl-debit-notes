import {
  createSlice,
  createAsyncThunk,
  AsyncThunk,
  PayloadAction,
} from "@reduxjs/toolkit";
import axios from "axios";
import type {
  CWDataResponse,
  DataSliceState,
  FetchDataResponse,
} from "./types";

export const fetchData: AsyncThunk<FetchDataResponse, string, {}> =
  createAsyncThunk("data/fetchData", async (fileName, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${process.env.API_URL}/V1/data`, {
        params: { file_name: fileName },
      });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || error.message);
    }
  });

export const fetchCWData: AsyncThunk<CWDataResponse[], string, {}> =
  createAsyncThunk(
    "data/fetchCWData",
    async (cw_status, { rejectWithValue }) => {
      try {
        const response = await axios.get(
          `${process.env.API_URL}/V1/data/CWUpload`,
          {
            params: { action_type: cw_status },
          }
        );
        return response.data;
      } catch (error: any) {
        return rejectWithValue(error.response?.data?.detail || error.message);
      }
    }
  );

const initialState: DataSliceState = {
  data: {},
  dataStatus: "idle",
  dataError: null,
  cwUploadData: [],
  cwUploadDataStatus: "idle",
  cwUploadDataError: null,
};

const dataSlice = createSlice({
  name: "data",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchData.pending, (state) => {
        state.dataStatus = "loading";
      })
      .addCase(
        fetchData.fulfilled,
        (state, action: PayloadAction<FetchDataResponse>) => {
          state.dataStatus = "succeeded";
          state.data = action.payload;
        }
      )
      .addCase(fetchData.rejected, (state, action) => {
        state.dataStatus = "failed";
        state.dataError = action.payload as string;
      })
      .addCase(fetchCWData.pending, (state) => {
        state.cwUploadDataStatus = "loading";
      })
      .addCase(
        fetchCWData.fulfilled,
        (state, action: PayloadAction<CWDataResponse[]>) => {
          state.cwUploadDataStatus = "succeeded";
          state.cwUploadData = action.payload;
        }
      )
      .addCase(fetchCWData.rejected, (state, action) => {
        state.cwUploadDataStatus = "failed";
        state.cwUploadDataError = action.payload as string;
      });
  },
});

export default dataSlice.reducer;
