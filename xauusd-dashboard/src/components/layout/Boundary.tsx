import { Component, type ErrorInfo, type ReactNode } from 'react'
import styles from './Boundary.module.css'

interface Props {
  children: ReactNode
  label?: string   // which area failed, e.g. "Macro Dashboard"
}

interface State {
  error: Error | null
}

/**
 * Classic error boundary. A single thrown render error (e.g. a malformed
 * session record hitting a parser) is contained to its tab instead of blanking
 * the whole app.
 */
export class Boundary extends Component<Props, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: Error): State {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // Surface in console for diagnosis; the UI shows a compact card.
    console.error(`[Boundary${this.props.label ? ` · ${this.props.label}` : ''}]`, error, info.componentStack)
  }

  handleReset = () => this.setState({ error: null })

  render() {
    if (this.state.error) {
      return (
        <div className={styles.card} role="alert">
          <div className={styles.title}>
            {this.props.label ? `${this.props.label} failed to render` : 'Something went wrong'}
          </div>
          <div className={styles.msg}>{this.state.error.message}</div>
          <button className={styles.btn} onClick={this.handleReset}>Try again</button>
        </div>
      )
    }
    return this.props.children
  }
}
