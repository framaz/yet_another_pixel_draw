import React from "react";
import ReactDOM from 'react-dom';

import Canvas from "./components/Canvas";
import UserName from "./components/UserName";

ReactDOM.render(
  <div>
    <Canvas />,
    <UserName loggedIn="{{ request.user.is_authenticated|lower }}" />
  </div>,
  root
)