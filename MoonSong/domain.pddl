(define (domain lunar)
    (:requirements :strips :typing)

    ; -------------------------------
    ; Types
    ; -------------------------------

    ; EXAMPLE

    ; (:types
    ;     parent_type
    ;     child_type - parent_type

    ; )
    (:types
        equipment
        rover - equipment
        lander - equipment
        location
        data
        scan - data
        image - data
        sample
    )

    ; -------------------------------
    ; Predicates
    ; -------------------------------

    ; EXAMPLE

    ; (:predicates
    ;     (no_arity_predicate)
    ;     (one_arity_predicate ?p - parameter_type)
    ; )

    (:predicates
        (is_landed ?lan - lander) ;If not then lander can choose a location to land
        (on_postion ?e - equipment ?l - location) ; equipment is on a location
        (is_connected ?l1 - location ?l2 - location) ; two locations are connected
        (has_picture ?l - location ?i - image) ; location has picture
        (has_sample ?l - location ?s - sample);This location has a sample
        (has_scan ?l - location ?sc - scan);This location has a scan ; data is captured
        (captured_data ?r - rover ?d - data)
        (collected_sample ?r - rover ?s - sample)
        (empty_memory ?r - rover);Rover is full, we can't hold more data
        (hand_empty ?r - rover)
        (is_full ?lan - lander) ;lander is full of sample
        (has_received ?d - data)
        (sample_got ?s - sample)
        
    )

    ; -------------------------------
    ; Actions
    ; -------------------------------

    ; EXAMPLE

    ; (:action action-template
    ;     :parameters (?p - parameter_type)
    ;     :precondition (and
    ;         (one_arity_predicate ?p)
    ;     )
    ;     :effect 
    ;     (and 
    ;         (no_arity_predicate)
    ;         (not (one_arity_predicate ?p))
    ;     )
    ; )

    (:action rover_land 
        :parameters (?lan - lander ?r - rover ?l - location)
        :precondition 
        (and
            (not (is_landed ?lan))
            )
        :effect 
        (and
            (is_landed ?lan)
            (on_postion ?lan ?l)
            (on_postion ?r ?l)
        )
    )
    
    (:action rover_move
        :parameters (?l1 - location ?l2 - location ?r - rover)
        :precondition
        (and
            (not (on_postion ?r ?l2))
            (on_postion ?r ?l1)
            (is_connected ?l1 ?l2)
        )
        :effect
        (and
            (not (on_postion ?r ?l1))
            (on_postion ?r ?l2)
        )
    )
    
    (:action take_picture
        :parameters (?r - rover ?l - location ?i - image)
        :precondition
        (and
            (on_postion ?r ?l)
            (has_picture ?l ?i)
            (empty_memory ?r)
        )
        :effect
        (and
            (not (empty_memory ?r))
            (not (has_picture ?l ?i))
            (captured_data ?r ?i)
        )
    )
    
    (:action take_scan
        :parameters (?r - rover ?l - location ?sc - scan)
        :precondition
        (and
            (on_postion ?r ?l)
            (has_scan ?l ?sc)
            (empty_memory ?r)
        )
        :effect
        (and
            (not (empty_memory ?r))
            (not (has_scan ?l ?sc))
            (captured_data ?r ?sc)
        )   
    )
    
    (:action take_sample
        :parameters (?r - rover ?l - location ?s - sample)
        :precondition
        (and
            (on_postion ?r ?l)
            (has_sample ?l ?s)
            (hand_empty ?r)
            
        )
        :effect
        (and
            (not (has_sample ?l ?s))
            (not (hand_empty ?r))
            (collected_sample ?r ?s)
        )
    )
    
    (:action transmit_data
        :parameters (?r - rover ?d - data)
        :precondition (and 
            (captured_data ?r ?d)
            (not (has_received ?d))
        ) 
        :effect (and
            (not (captured_data ?r ?d))
            (has_received ?d)
            (empty_memory ?r)
        )
    )
    
    (:action sample_receive
        :parameters (?lan - lander ?r - rover ?s - sample ?l - location)
        :precondition (and
            (not (is_full ?lan))
            (on_postion ?r ?l)
            (on_postion ?lan ?l)
            (collected_sample ?r ?s)
         )
        :effect (and 
            (is_full ?lan)
            (not (collected_sample ?r ?s))
            (hand_empty ?r)
            (sample_got ?s)
        )
    )
    

        )