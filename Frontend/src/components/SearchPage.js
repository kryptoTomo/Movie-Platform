import axios from "./../axios";
import { Fragment, useEffect, useState } from "react";
import { Form, Col, Row, Button, Table} from "react-bootstrap";
import './styles.css';


const SearchPage = (props) => {

    const [films, setFilms] = useState([]);
    const [liked, setLiked] = useState([]);
    const [payload, setPayload] = useState();

    useEffect(()=>{
        handleLoadData();
        var body = {
            cuisine: "",
            location: "",
            person: ""
        };
        setPayload(body)
        axios.post("/get-films", {cuisine:"",location: "",person: ""})
        .then(res => {
            console.log(res.data.films)
            setFilms(res.data.films)
        }).catch(err => {
            console.log(err.message)
        })
    }, [])

    const handleLoadData = () => {
        axios.post("/get-films", {cuisine:"",location: "",person: props.userName})
        .then(res => {
            setLiked(res.data.films.map(res => res.film))
        }).catch(err => {
            console.log(err.message)
        })
    }

    const handleRemoveFilm = (name) => {
        axios.post("/dislike", {person: props.userName, film: name})
        .then(res => {
            handleRefreshSfterChange()
        }).catch(err => {
            console.log(err.message)
        })
    }

    const handleAddFilm = (name) => {
        axios.post("/like", {person: props.userName, film: name})
        .then(res => {
            handleRefreshSfterChange()
        }).catch(err => {
            console.log(err.message)
        })
    }

    const handleSubmitForm = (event) => {
        event.preventDefault()
        var param = event.target[0].value;
        var value = event.target[1].value;
        var body = {
            cuisine: "",
            location: "",
            person: ""
        };
        switch(param){
            case("cui"):
                body = {
                    cuisine: value,
                    location: "",
                    person: ""
                }
                break;
            case("loc"):
                body = {
                    cuisine: "",
                    location: value,
                    person: ""
                }
                break;
            case("lik"):
                body = {
                    cuisine: "",
                    location: "",
                    person: value
                }
            break;
            default:
        }
        setPayload(body)
        axios.post("/get-films", body)
        .then(res => {
            console.log(res.data.films)
            setFilms(res.data.films)
        }).catch(err => {
            console.log(err.message)
        })
    }

    const handleRefreshSfterChange = () => {
        axios.post("/get-films", payload)
        .then(res => {
            console.log(res.data.films)
            handleLoadData()
            setFilms(res.data.films)
        }).catch(err => {
            console.log(err.message)
        })
    }

    let rows = films.map((res, index) => {
        return (
            <tr>
                <td>{index+1}</td>
                <td>{res.film}</td>
                <td>{res.location}</td>
                <td>{res.cuisine}</td>
                <td>{liked.includes(res.film) 
                ? <Button variant="dark" onClick={() => handleRemoveFilm(res.film)} >Cofnij polubienie</Button>
                : <Button variant="dark" onClick={() => handleAddFilm(res.film)} >Polub</Button>}</td>
            </tr>)
    })
    
    return (
        <Fragment>
            <Form className="SearchForm" onSubmit={handleSubmitForm}>
                <Form.Group as={Row} controlId="formHorizontalType">
                    <Form.Label>
                    Wyszukaj filtrując po: 
                    </Form.Label>
                    <Col sm={2}>
                        <Form.Select required >
                            <option value="loc">Studio</option>
                            <option value="cui">Gatunek Filmowy</option>
                            <option value="lik">Polubione przez</option>
                        </Form.Select>
                    </Col>
                    <Col sm={3}>
                        <Form.Control placeholder="Wpisz szukaną wartość parametru..." type="text" required/>
                    </Col>
                    <Col sm={1}>
                        <Button variant="dark" type="submit" >
                            Szukaj
                        </Button>
                    </Col>
                </Form.Group>
            </Form>

            <Table striped bordered hover className="FilmTable">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Tytuł</th>
                        <th>Studio</th>
                        <th>Gatunek Filmowy</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </Table>
        </Fragment>
    );
}

export default SearchPage;