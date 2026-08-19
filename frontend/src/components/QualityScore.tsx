export function QualityScore({score}:{score:number}) {
 return <div className="quality-score" style={{"--score":`${score*3.6}deg`} as React.CSSProperties}><div><strong>{score.toFixed(1)}%</strong><span>quality score</span></div></div>;
}