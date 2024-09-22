import { combineReducers } from "@reduxjs/toolkit";
// slices
import { emailSlice, fileSlice, dataSlice, actionSlice } from "./slices";

const rootReducer = combineReducers({
  email: emailSlice,
  file: fileSlice,
  data: dataSlice,
  action: actionSlice,
});

export default rootReducer;
