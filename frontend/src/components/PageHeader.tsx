export function PageHeader({ title, description }: { title: string; description: string }) {
  return <header className="page-header"><div><p className="eyebrow">Data · Software</p><h2>{title}</h2><p>{description}</p></div></header>;
}
