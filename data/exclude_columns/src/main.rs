use std::fmt::Debug;
use std::io;
use csv::{ReaderBuilder, WriterBuilder};

fn sort_like_example<T: PartialEq>(target: &mut Vec<T>, example: &Vec<T>) {
    assert_eq!(target.len() <= example.len(), true);
    let mut new_len = 0usize;
    for finding in example {
        for checking in new_len..target.len() {
            if *finding == target[checking] {
                target.swap(new_len, checking);
                new_len += 1;
            }
        }
    }

    unsafe {
        target.set_len(new_len);
    }
}

#[derive(Debug, Default, serde::Deserialize)]
struct Record {
    data: Vec<String> 
}

fn main() {
    let read_from = "/home/alexe/Загрузки/final_merged.csv";
    let rdr = ReaderBuilder::new().delimiter(',' as u8).from_path(read_from);
    let headers: Vec<String> = rdr.unwrap().headers().unwrap().deserialize(None).unwrap();
    
    let rdr = ReaderBuilder::new().delimiter(',' as u8).from_path(read_from);
    let mut useful_headers: Vec<String> = vec![];
    println!("Write number of which columns to keep, double enter to exit:");
    headers.iter().enumerate().for_each(|(num, x)| {
        println!("{num} - {x}")
    });
    loop {
        let mut r = String::default();
        io::stdin().read_line(&mut r).expect("Worst");
        if r.trim().bytes().nth(0).unwrap_or('\n' as u8) == '\n' as u8 {
            break;
        }
        if let Ok(input) = r.trim().parse::<i32>() {
            if input >= 0 && input < headers.len() as i32 {
                useful_headers.push(headers[input as usize].clone());
                println!("Successfully added")
            }
            else {
                println!("{input} is out of bounds")
            }
        }
        else {
            println!("Bad input, try again:")
        }
    }
    
    sort_like_example(&mut useful_headers, &headers);
    let mut add_headers= vec![];
    println!("Type names of new columns to add, double enter to exit:");
    loop {
        let mut r = String::default();
        io::stdin().read_line(&mut r).expect("Worst");
        r = r.trim().to_string();
        if r.trim().bytes().nth(0).unwrap_or('\n' as u8) == '\n' as u8 {
            break;
        }
        useful_headers.push(r);
        let mut s1 = String::default();
        let mut s2 = String::default();
        println!("{} = $1 / $2", useful_headers.last().as_ref().unwrap());
        io::stdin().read_line(&mut s1).unwrap();
        io::stdin().read_line(&mut s2).unwrap();
        if let Ok(n1) = s1.trim().parse::<usize>() && let Ok(n2) = s2.trim().parse::<usize>() {
            if n1 < headers.len() && n2 < headers.len() {
                add_headers.push((n1, n2))
            }
        }
        println!("Added")
    }
    
    
    let mut book: Vec<Record> = vec![];
    for result in rdr.unwrap().records() { 
        let new_record: Record = result.unwrap().deserialize(None).unwrap();
        let mut useful_record: Record = Record::default();
        for (num, x) in new_record.data.iter().enumerate() {
            if useful_headers
                .iter()
                .find(|x| {
                    **x == headers[num]
                })
                .is_some()  {
                if new_record.data[num] != "" {
                    useful_record.data.push(x.clone());
                }
                else {
                    useful_record.data.push("0".to_string())
                }
            }
        }
        let mut new_column = 0usize;
        while useful_record.data.len() < useful_headers.len() {
            let first = &new_record.data[add_headers[new_column].0];
            let second = &new_record.data[add_headers[new_column].1];
            let n1 = first.trim().parse::<f32>().unwrap_or(0f32);
            let n2 = second.trim().parse::<f32>().unwrap_or(1f32);
            useful_record.data.push((n1 / n2).to_string());
            
            new_column += 1;
        }
        book.push(useful_record);
    }
    
    /*let read_from = "/home/alexe/Загрузки/only_rating.csv";
    let add = ReaderBuilder::new().delimiter(',' as u8).from_path(read_from);
    let mut add_headers: Vec<String> = add.unwrap().headers().unwrap().deserialize(None).unwrap();

    let add = ReaderBuilder::new().delimiter(',' as u8).from_path(read_from);
    
    for (num, record) in add.unwrap().records().enumerate() {
        let new_record: Record = record.unwrap().deserialize(None).unwrap();
        let mut add_data = new_record.data;
        book[num].data.append(&mut add_data)
    }
    useful_headers.append(&mut add_headers);*/
    
    println!("{:?}", useful_headers);
    
    let mut wrt = WriterBuilder::new().delimiter(',' as u8).from_path("/home/alexe/training.csv");
    wrt.as_mut().unwrap().write_record(useful_headers).unwrap();

    for row in &book {
        wrt.as_mut().unwrap().write_record(&row.data).unwrap();
    }
    wrt.unwrap().flush().unwrap();
}
