export function convert24To12(time24: string): string {
    const [hoursStr, minutesStr] = time24.split(':');
    let hours = parseInt(hoursStr, 10);
    const minutes = parseInt(minutesStr, 10);

    if (isNaN(hours) || isNaN(minutes)) {
        throw new Error("Invalid time format. Expected 'HH:MM'");
    }

    const period = hours >= 12 ? 'PM' : 'AM';
    
    // Convert 24h to 12h format
    hours = hours % 12;
    hours = hours ? hours : 12;

    const formattedMinutes = minutes.toString().padStart(2, '0');

    return `${hours}:${formattedMinutes} ${period}`;
}