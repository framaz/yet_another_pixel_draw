import React from "react";

export default class LoginForm extends React.Component {
  constructor(props) {
    super(props);

    this.loginSuccess = props.loginSuccess;

    this.state = { hideWrongPassword: true
    }
    this.formRef = React.createRef();
    this._handleSubmit = this._handleSubmit.bind(this);
  }
  async _handleSubmit(e) {
    e.preventDefault();
    var loginForm = this.formRef.current;
    var data = FormSerialize.serialize(loginForm);

    var csrf = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    document.cookie = "csrftoken=" + csrf;
    data += "&next=" + frontend_url;
    var response = await fetch(login_url, {
      method: 'POST',
      headers: {
      "Content-type": "application/x-www-form-urlencoded",
      "X-CSRFToken": csrf,
      },
      body: data,
      redirect: "manual"
    });
    if (response.type != "opaqueredirect")
      this.setState({hideWrongPassword: false})
    else
      this.loginSuccess();

  }
  render() {
    return (
      <form className="form" onSubmit={this._handleSubmit} ref={this.formRef} action=''>
        <table>
          <tr>
            <td>
              <label for="id_username">Username:</label>
            </td>
            <td>
              <input
                type="text"
                name="username"
                autocapitalize="none"
                autocomplete="username"
                maxlength="150"
                required
                id="id_username"
              />
            </td>
          </tr>
          <tr>
            <td>
              <label for="id_password">Password:</label>
            </td>
            <td>
              <input
                type="password"
                name="password"
                autocomplete="current-password"
                required
                id="id_password"
              />
            </td>
          </tr>
        </table>

        <input type="submit" value="login" />
        <text hidden={this.state.hideWrongPassword}> Wrong Password </text>
      </form>
    );
  }
}
