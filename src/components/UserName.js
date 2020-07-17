import React from "react";

import LoginForm from "./LoginForm";

export default class UserName extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      loggedIn: props.loggedIn === "true",
    };
    this.loginSuccess = this.loginSuccess.bind(this);
  }
  loginSuccess () {
    this.setState ({
      loggedIn: true,
    });
  }
  render() {
    if (this.state.loggedIn) {
      return (
        <div class="UserCred" >
          <br />
        </div>
      );
    } else {
      return (
        <div class="UserCred" >
          <LoginForm loginSuccess={this.loginSuccess}/>
        </div>
      );
    }
  }
}