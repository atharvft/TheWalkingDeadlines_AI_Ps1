import { Link, NavLink } from 'react-router-dom'

const paths = {
  grid: <><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></>,
  bag: <><path d="M6 8h12l1 12H5L6 8Z"/><path d="M9 8a3 3 0 0 1 6 0"/></>,
  spark: <><path d="m12 3 1.3 5.7L19 10l-5.7 1.3L12 17l-1.3-5.7L5 10l5.7-1.3L12 3Z"/><path d="m19 16 .6 2.4L22 19l-2.4.6L19 22l-.6-2.4L16 19l2.4-.6L19 16Z"/></>,
  help: <><circle cx="12" cy="12" r="9"/><path d="M9.6 9a2.5 2.5 0 1 1 4 2c-.9.6-1.6 1-1.6 2.2"/><path d="M12 17h.01"/></>,
  package: <><path d="m4 7 8-4 8 4-8 4-8-4Z"/><path d="M4 7v10l8 4 8-4V7M12 11v10"/></>,
  warehouse: <><path d="m3 10 9-7 9 7v10H3V10Z"/><path d="M7 20v-6h10v6M8 10h.01M12 10h.01M16 10h.01"/></>,
  users: <><circle cx="9" cy="8" r="3"/><path d="M3 20c.4-3.3 2.4-5 6-5s5.6 1.7 6 5"/><path d="M16 5.2a3 3 0 0 1 0 5.7M17 15c2.2.3 3.5 2 3.8 4.5"/></>,
  truck: <><path d="M3 6h11v11H3zM14 10h4l3 3v4h-7z"/><circle cx="7" cy="19" r="2"/><circle cx="18" cy="19" r="2"/></>,
  receipt: <><path d="M6 3h12v18l-3-2-3 2-3-2-3 2V3Z"/><path d="M9 8h6M9 12h6M9 16h3"/></>,
  chart: <><path d="M4 19V5M4 19h16"/><path d="m7 15 3-4 3 2 5-7"/></>,
  gear: <><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-1.9 1.9-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.1h-2.7v-.1a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1-1.9-1.9.1-.1A1.7 1.7 0 0 0 7.7 15a1.7 1.7 0 0 0-1.6-1H6v-2.7h.1a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9l-.1-.1 1.9-1.9.1.1a1.7 1.7 0 0 0 1.9.3 1.7 1.7 0 0 0 1-1.6V6h2.7v.1a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1 1.9 1.9-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.1V14h-.1a1.7 1.7 0 0 0-1.6 1Z"/></>,
  search: <><circle cx="10.8" cy="10.8" r="6.8"/><path d="m16 16 4 4"/></>,
  bell: <><path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4"/></>,
  plus: <><path d="M12 5v14M5 12h14"/></>,
  mic: <><rect x="8" y="3" width="8" height="12" rx="4"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3M9 21h6"/></>,
  send: <><path d="m3 11 18-8-8 18-2-8-8-2Z"/><path d="m11 13 5-5"/></>,
  check: <><path d="m5 12 4 4L19 6"/></>,
  arrow: <><path d="M5 12h14M13 6l6 6-6 6"/></>,
  filter: <><path d="M4 6h16M7 12h10M10 18h4"/></>,
  more: <><circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/></>,
  chevron: <path d="m9 18 6-6-6-6"/>
}

export function Icon({ name, size = 16, strokeWidth = 1.8 }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name] || paths.grid}</svg>
}

export function Button({ children, variant = 'primary', icon, ...props }) {
  return <button className={`btn btn-${variant}`} {...props}>{icon && <Icon name={icon} size={14}/>} {children}</button>
}

export function PageHeader({ eyebrow, title, subtitle, actions }) {
  return <div className="page-heading"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1>{subtitle && <p>{subtitle}</p>}</div>{actions && <div className="heading-actions">{actions}</div>}</div>
}

export function StatusBadge({ status }) {
  const normalized = status.toLowerCase()
  let tone = normalized.includes('clar') || normalized.includes('pending') || normalized.includes('low') ? 'pending' : normalized.includes('out') ? 'out' : normalized.includes('pack') ? 'packing' : normalized.includes('deliver') ? 'delivered' : normalized.includes('cancel') ? 'cancelled' : 'confirmed'
  return <span className={`status ${tone}`}>{status}</span>
}

export const navGroups = [
  { label: 'Workspace', items: [{ label:'Overview', to:'/', icon:'grid' }, { label:'Orders', to:'/orders', icon:'bag' }, { label:'AI Order Desk', to:'/ai-desk', icon:'spark', ai:true }, { label:'Clarifications', to:'/clarifications', icon:'help' }] },
  { label: 'Store', items: [{ label:'Products', to:'/products', icon:'package' }, { label:'Inventory', to:'/inventory', icon:'warehouse' }, { label:'Customers', to:'/customers', icon:'users' }, { label:'Deliveries', to:'/deliveries', icon:'truck' }] },
  { label: 'Manage', items: [{ label:'Billing', to:'/billing', icon:'receipt' }, { label:'Analytics', to:'/analytics', icon:'chart' }, { label:'Settings', to:'/settings', icon:'gear' }] }
]

export function AppShell({ children }) {
  return <div className="app-shell"><aside className="sidebar"><Link className="brand" to="/"><div className="brand-mark">g</div><div className="brand-name">gully<span>cart</span></div></Link>{navGroups.map(group => <div key={group.label} style={{marginBottom:22}}><div className="nav-label">{group.label}</div><nav className="nav">{group.items.map(item => <NavLink end={item.to === '/'} key={item.to} className={({isActive}) => `nav-link ${isActive ? 'active' : ''} ${item.ai ? 'ai' : ''}`} to={item.to}><i className="nav-icon"><Icon name={item.icon} size={15}/></i><span>{item.label}</span></NavLink>)}</nav></div>)}<div className="sidebar-spacer"/><div className="store-card"><strong>Shree Ganesh Kirana</strong><p>Open · Last synced just now</p></div><div className="profile-mini"><div className="avatar">AS</div><div><strong>Arjun Shah</strong><span>Store owner</span></div></div></aside><div className="main-shell"><header className="topbar"><div className="topbar-context"><span>Store workspace</span><b> / </b><b>Shree Ganesh Kirana</b></div><div className="topbar-actions"><button className="icon-btn"><Icon name="search" size={16}/></button><button className="icon-btn notification-dot"><Icon name="bell" size={16}/></button><div className="avatar" style={{width:30,height:30}}>AS</div></div></header><main className="main-content">{children}</main></div></div>
}
