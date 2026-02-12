import React from "react";

function AuthForm({
  token,
  email,
  password,
  onEmailChange,
  onPasswordChange,
  onLogin,
  onGoogle,
  onLogout,
  oauthProcessing,
  onOpenGoogleModal
}) {
  if (token) {
    return (
      <div className="auth-logged">
        <span className="pill">Authenticated</span>
        <button type="button" onClick={onLogout}>Logout</button>
      </div>
    );
  }

  return (
    <form onSubmit={onLogin} className="auth-form">
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => onEmailChange(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => onPasswordChange(e.target.value)}
        required
      />
      <button type="submit">Login</button>
      <button
        type="button"
        className="ghost"
        onClick={onOpenGoogleModal || onGoogle}
        disabled={oauthProcessing}
      >
        {oauthProcessing ? "Processing..." : "Login with Google"}
      </button>
    </form>
  );
}

export default AuthForm;
